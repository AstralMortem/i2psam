from dataclasses import dataclass
import asyncio
from typing import TYPE_CHECKING
from i2psam.utils import tokenize_sam_line
from i2psam.logs import get_logger

if TYPE_CHECKING:
    from .session import Session

logger = get_logger("datagram")


@dataclass
class Datagram:
    session: "Session"
    queue: asyncio.Queue[tuple[str, bytes]]
    send_transport: asyncio.DatagramTransport

    def sendto(
        self, destination: str, payload: bytes, *, sam_version_line: str = "3.0"
    ) -> None:
        # Datagram header format to UDP 7655:
        # "3.0 $nickname $destination [opts]\n" then payload :contentReference[oaicite:24]{index=24}
        header = f"{sam_version_line} {self.session.session_id} {destination}\n".encode(
            "utf-8"
        )
        logger.debug(
            "Sending datagram session=%s destination=%s payload_len=%s",
            self.session.session_id,
            destination,
            len(payload),
        )
        self.send_transport.sendto(header + payload)

    async def recv(self) -> tuple[str, bytes]:
        return await self.queue.get()


class SAMDatagramProtocol(asyncio.DatagramProtocol):
    queue: asyncio.Queue[tuple[str, bytes]]

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport

    def datagram_received(self, data: bytes, addr) -> None:
        # Forwarded repliable datagrams are prefixed with:
        # "$destination FROM_PORT=.. TO_PORT=..\n$payload" :contentReference[oaicite:21]{index=21}
        try:
            head, payload = data.split(b"\n", 1)
            head_tokens = tokenize_sam_line(head.decode("utf-8", errors="replace"))
            sender_dest = head_tokens[0] if head_tokens else ""
            logger.debug(
                "Received datagram from sender=%s payload_len=%s",
                sender_dest,
                len(payload),
            )
            self.queue.put_nowait((sender_dest, payload))
        except ValueError:
            # No newline: treat whole thing as payload with unknown sender
            logger.debug("Received datagram without header payload_len=%s", len(data))
            self.queue.put_nowait(("", data))

    @classmethod
    def with_q(cls, queue: asyncio.Queue[tuple[str, bytes]]):
        instance = cls()
        instance.queue = queue
        return instance
