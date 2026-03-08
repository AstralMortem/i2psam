import asyncio
from i2psam.exceptions import SAMStreamError, SAMError
from i2psam.logs import get_logger
from dataclasses import dataclass
from i2psam import commands
from i2psam.types import SessionStyle
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, cast
from .datagram import SAMDatagramProtocol, Datagram

if TYPE_CHECKING:
    from .client import SAMClient
    from .connection import Connection

logger = get_logger("session")


@dataclass
class Session:
    client: "SAMClient"
    conn: "Connection"
    session_id: str
    priv_destination: str | None

    @asynccontextmanager
    async def connect_stream(self, destination: str, silent: bool = False):
        logger.debug("Opening stream connection for session=%s", self.session_id)
        async with self.client.connection() as conn:
            msg = commands.StreamConnect(
                ID=self.session_id, DESTINATION=destination, SILENT=silent
            )

            response = await conn.request(msg)
            if not response.is_ok:
                logger.warning(
                    "Stream connect failed for session=%s: %s",
                    self.session_id,
                    response.message,
                )
                raise SAMStreamError(f"Unable to create stream: {response.message}")

            yield conn

    @asynccontextmanager
    async def accept_stream(self, silent: bool = False):
        logger.debug("Accepting stream for session=%s", self.session_id)
        async with self.client.connection() as conn:
            msg = commands.StreamAccept(ID=self.session_id, SILENT=silent)

            response = await conn.request(msg)
            if not response.is_ok:
                logger.warning(
                    "Stream accept failed for session=%s: %s",
                    self.session_id,
                    response.message,
                )
                raise SAMStreamError(f"Unable to accept stream: {response.message}")

            dest = None
            if not silent:
                dest = await conn.read_line()

            yield dest, conn

    @asynccontextmanager
    async def forward_stream(
        self, port: int, host: str | None = None, silent: bool = False, **kw
    ):
        logger.debug(
            "Forwarding stream for session=%s to %s:%s", self.session_id, host, port
        )
        async with self.client.connection() as conn:
            msg = commands.StreamForward(
                ID=self.session_id, PORT=port, HOST=host, SILENT=silent, **kw
            )
            response = await conn.request(msg)

            if not response.is_ok:
                logger.warning(
                    "Stream forward failed for session=%s: %s",
                    self.session_id,
                    response.message,
                )
                raise SAMStreamError(f"Unable to forward stream: {response.message}")

            dest = None
            if not silent:
                dest = await conn.read_line()

            yield dest, conn

    @asynccontextmanager
    async def create_datagram(
        self,
        bind_host: str = "127.0.0.1",
        bind_port: int = 0,  # 0 = random local UDP
        forward: bool = True,
    ):
        logger.debug("Creating datagram endpoints for session=%s", self.session_id)
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[tuple[str, bytes]] = asyncio.Queue()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: SAMDatagramProtocol.with_q(queue), local_addr=(bind_host, bind_port)
        )
        transport = cast(asyncio.DatagramTransport, transport)
        local_port = transport.get_extra_info("sockname")[1]

        create = commands.SessionCreate(
            STYLE=SessionStyle.DATAGRAM,
            ID=self.session_id,
            DESTINATION=self.priv_destination,
            PORT=local_port if forward else None,
            HOST=bind_host if forward else None,
        )

        status = await self.conn.request(create)
        if not status.is_ok:
            transport.close()
            logger.error(
                "Datagram session creation failed for session=%s: %s",
                self.session_id,
                status.message,
            )
            raise SAMError(f"DATAGRAM SESSION could not be created: {status.message}")

        send_transport, _ = await loop.create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(),
            remote_addr=(self.client.cfg.host, self.client.cfg.udp_port),
        )
        send_transport = cast(asyncio.DatagramTransport, send_transport)

        try:
            yield Datagram(self, queue, send_transport)
        finally:
            send_transport.close()
            transport.close()
