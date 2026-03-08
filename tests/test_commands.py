import pytest

from i2psam.commands import HelloReply, HelloVersion, StreamConnect
from i2psam.exceptions import SAMError
from i2psam.types import Result


def test_hello_version_to_message_with_newline_and_fields():
    msg = HelloVersion(MIN="3.0", MAX="3.3", USER="alice")
    line = msg.to_message()

    assert line.endswith("\n")
    assert line.startswith("HELLO VERSION")
    assert "MIN=3.0" in line
    assert "MAX=3.3" in line
    assert "USER=alice" in line


def test_hello_reply_parse_success():
    reply = HelloReply.parse("HELLO REPLY RESULT=OK VERSION=3.1\n")
    assert reply.result == Result.OK
    assert reply.version == "3.1"
    assert reply.is_ok is True


def test_hello_reply_parse_unexpected_command_raises():
    with pytest.raises(SAMError):
        HelloReply.parse("STREAM STATUS RESULT=OK\n")


def test_command_parse_response_uses_response_class():
    parsed = StreamConnect.parse_response("STREAM STATUS RESULT=OK\n")
    assert parsed.result == Result.OK
