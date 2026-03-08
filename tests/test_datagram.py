import asyncio

from i2psam.client.datagram import Datagram, SAMDatagramProtocol


class DummySession:
    session_id = "sess1"


class FakeDatagramTransport:
    def __init__(self):
        self.payloads = []

    def sendto(self, data: bytes):
        self.payloads.append(data)


def test_datagram_sendto_builds_header_plus_payload():
    transport = FakeDatagramTransport()
    q: asyncio.Queue[tuple[str, bytes]] = asyncio.Queue()
    datagram = Datagram(DummySession(), q, transport)

    datagram.sendto("destX", b"hello")

    assert transport.payloads == [b"3.0 sess1 destX\nhello"]


def test_protocol_datagram_received_parses_sender_and_payload():
    q: asyncio.Queue[tuple[str, bytes]] = asyncio.Queue()
    proto = SAMDatagramProtocol.with_q(q)

    proto.datagram_received(b"abcDest FROM_PORT=123 TO_PORT=321\nPING", None)

    sender, payload = q.get_nowait()
    assert sender == "abcDest"
    assert payload == b"PING"


def test_protocol_datagram_received_without_newline_uses_empty_sender():
    q: asyncio.Queue[tuple[str, bytes]] = asyncio.Queue()
    proto = SAMDatagramProtocol.with_q(q)

    proto.datagram_received(b"rawpayload", None)

    sender, payload = q.get_nowait()
    assert sender == ""
    assert payload == b"rawpayload"
