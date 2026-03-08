import asyncio

import pytest

from i2psam.client.connection import Connection
from i2psam.commands import HelloVersion
from i2psam.exceptions import SAMClientError


class DummyClient:
    cfg = object()


class FakeReader:
    def __init__(self, read_data: bytes = b"", line_data: bytes = b""):
        self._read_data = read_data
        self._line_data = line_data

    async def read(self, _length=-1):
        data = self._read_data
        self._read_data = b""
        return data

    async def readline(self):
        data = self._line_data
        self._line_data = b""
        return data


class FakeWriter:
    def __init__(self):
        self.writes = []
        self.closed = False

    def write(self, data: bytes):
        self.writes.append(data)

    async def drain(self):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        return None


@pytest.mark.parametrize("method", ["read", "read_line"])
def test_read_methods_raise_on_closed_stream(method):
    conn = Connection(DummyClient(), FakeReader(), FakeWriter())

    async def run():
        if method == "read":
            await conn.read()
        else:
            await conn.read_line()

    with pytest.raises(SAMClientError):
        asyncio.run(run())


def test_write_appends_newline_for_string_payload():
    writer = FakeWriter()
    conn = Connection(DummyClient(), FakeReader(), writer)

    asyncio.run(conn.write("HELLO VERSION"))

    assert writer.writes[-1] == b"HELLO VERSION\n"


def test_request_roundtrip_parses_response():
    reader = FakeReader(line_data=b"HELLO REPLY RESULT=OK VERSION=3.1\n")
    writer = FakeWriter()
    conn = Connection(DummyClient(), reader, writer)

    reply = asyncio.run(conn.request(HelloVersion(MIN="3.0", MAX="3.3")))

    assert reply.version == "3.1"
    assert writer.writes
    assert writer.writes[-1].startswith(b"HELLO VERSION")


def test_close_resets_reader_writer_refs():
    reader = FakeReader(line_data=b"x")
    writer = FakeWriter()
    conn = Connection(DummyClient(), reader, writer)

    asyncio.run(conn.close())

    assert writer.closed is True
    assert conn.reader is None
    assert conn.writer is None
