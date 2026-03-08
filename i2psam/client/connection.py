from dataclasses import dataclass
import asyncio
from typing import TYPE_CHECKING, Literal
from i2psam import commands
from i2psam.types import SessionStyle
from i2psam.commands.base import I2PCommand, R
from i2psam.exceptions import SAMClientError
from i2psam.logs import get_logger
from .session import Session

if TYPE_CHECKING:
    from .client import SAMClient

logger = get_logger("connection")


@dataclass
class Connection:
    client: "SAMClient"
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    @property
    def cfg(self):
        if self.client:
            return self.client.cfg

    async def read(self, length: int | None = -1) -> bytes:
        data = await self.reader.read(length)
        if not data:
            logger.debug("SAM bridge closed connection while reading %s bytes", length)
            raise SAMClientError("SAM Bridge close connection")
        return data

    async def read_line(self) -> bytes:
        data = await self.reader.readline()
        if not data:
            logger.debug("SAM bridge closed connection while reading line")
            raise SAMClientError("SAM Bridge close connection")
        return data

    async def read_string(self) -> str:
        data = await self.read_line()
        return data.decode("utf-8")

    async def write(self, line: str | bytes):
        if isinstance(line, str):
            line = line.encode("utf-8")

        if not line.endswith(b"\n"):
            line = line + b"\n"

        logger.debug(
            "Sending SAM line: %s", line.decode("utf-8", errors="replace").rstrip()
        )
        self.writer.write(line)
        await self.writer.drain()

    async def request(self, msg: I2PCommand[R]) -> R:
        await self.write(msg.to_bytes())
        response = await self.read_line()
        logger.debug(
            "Received SAM reply: %s",
            response.decode("utf-8", errors="replace").rstrip(),
        )
        return msg.parse_response(response)

    async def raw_request(self, msg: str | bytes) -> str:
        await self.write(msg)
        response = await self.read_line()
        logger.debug("Received raw SAM reply")
        return response.decode("utf-8")

    async def create_session(
        self,
        session_id: str,
        destination: str | Literal["TRANSIENT"],
        style: SessionStyle = SessionStyle.STREAM,
        **kw,
    ):
        msg = commands.SessionCreate(
            ID=session_id,
            DESTINATION=destination,
            STYLE=style,
            SIGNATURE_TYPE=kw.get("SIGNATURE_TYPE", self.cfg.signature_type),
            **kw,
        )

        response = await self.request(msg)
        if not response.is_ok:
            logger.error(f"Unable to create session: {response.message}")
            raise SAMClientError(f"Unable to create session: {response.message}")

        return Session(self.client, self, session_id, response.destination)

    async def dest_generate(self, **kw):
        return await self.request(
            commands.DestGenerate(
                SIGNATURE_TYPE=kw.get("SIGNATURE_TYPE", self.cfg.signature_type)
            )
        )

    async def handshake(self, **kw):
        return await self.request(
            commands.HelloVersion(
                MIN=kw.get("MIN", self.cfg.min_version),
                MAX=kw.get("MAX", self.cfg.max_version),
                USER=kw.get("USER", self.cfg.user),
                PASSWORD=kw.get("PASSWORD", self.cfg.password),
                **kw,
            )
        )

    async def naming_lookup(self, name: str, **kw):
        return await self.request(commands.NamingLookup(NAME=name, **kw))

    async def close(self):
        if self.writer:
            logger.debug("Closing SAM connection")
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                logger.exception("Error while closing SAM writer")
                pass

        self.writer = None
        self.reader = None
