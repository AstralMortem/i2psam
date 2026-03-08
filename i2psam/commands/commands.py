from .base import I2PCommand, I2PReply
from pydantic import Field, model_validator
from typing import Literal
from i2psam.types import SessionStyle, SigningKeyType


class HelloReply(I2PReply):
    command = "HELLO"
    subcommand = "REPLY"
    version: str = Field(alias="VERSION")


class HelloVersion(I2PCommand[HelloReply]):
    response_class = HelloReply
    command = "HELLO"
    subcommand = "VERSION"

    min: str | None = Field(default=None, alias="MIN")
    max: str | None = Field(default=None, alias="MAX")
    user: str | None = Field(default=None, alias="USER")
    password: str | None = Field(default=None, alias="PASSWORD")


class SessionReply(I2PReply):
    command = "SESSION"
    subcommand = "STATUS"
    destination: str | None = Field(default=None, alias="DESTINATION")


class SessionCreate(I2PCommand[SessionReply]):
    response_class = SessionReply
    command = "SESSION"
    subcommand = "CREATE"

    style: SessionStyle = Field(default=SessionStyle.STREAM, alias="STYLE")
    id: str = Field(alias="ID")
    destination: str | Literal["TRANSIENT"] = Field(alias="DESTINATION")
    signature_type: SigningKeyType | None = Field(
        default=SigningKeyType.EDDSA_SHA512_ED25519, alias="SIGNATURE_TYPE"
    )
    port: int | None = Field(default=None, alias="PORT")
    host: int | None = Field(default=None, alias="HOST")
    from_port: int | None = Field(default=None, alias="FROM_PORT")
    to_port: int | None = Field(default=None, alias="TO_PORT")
    protocol: int | None = Field(default=None, alias="PROTOCOL")
    i2cp_leaseSetEncType: str | None = Field(
        default="4,0", alias="i2cp.leaseSetEncType"
    )

    @model_validator(mode="after")
    def _validate_session(self):
        return self


class StreamStatus(I2PReply):
    command = "STREAM"
    subcommand = "STATUS"


class StreamConnect(I2PCommand[StreamStatus]):
    response_class = StreamStatus
    command = "STREAM"
    subcommand = "CONNECT"
    id: str = Field(alias="ID")
    destination: str = Field(alias="DESTINATION")
    silent: bool = Field(alias="SILENT", default=False)


class StreamAccept(I2PCommand[StreamStatus]):
    response_class = StreamStatus
    command = "STREAM"
    subcommand = "ACCEPT"
    id: str = Field(alias="ID")
    silent: bool = Field(alias="SILENT", default=False)


class StreamForward(I2PCommand[StreamStatus]):
    response_class = StreamStatus
    command = "STREAM"
    subcommand = "FORWARD"
    id: str = Field(alias="ID")
    port: int = Field(alias="PORT")
    host: str | None = Field(alias="HOST", default=None)
    silent: bool | None = Field(alias="SILENT", default=None)
    ssl: bool | None = Field(alias="SSL", default=None)


class DestReply(I2PReply):
    command = "DEST"
    subcommand = "REPLY"
    pub: str = Field(alias="PUB")
    priv: str = Field(alias="PRIV")


class DestGenerate(I2PCommand[DestReply]):
    response_class = DestReply
    command = "DEST"
    subcommand = "GENERATE"
    signature_type: SigningKeyType | None = Field(
        alias="SIGNATURE_TYPE", default=SigningKeyType.EDDSA_SHA512_ED25519
    )


class NamingReply(I2PReply):
    command = "NAMING"
    subcommand = "REPLY"
    name: str = Field(alias="NAME")
    value: str | None = Field(alias="VALUE")


class NamingLookup(I2PCommand[NamingReply]):
    response_class = NamingReply
    command = "NAMING"
    subcommand = "LOOKUP"
    name: str = Field(alias="NAME")
    options: bool | None = Field(alias="OPTIONS", default=None)
