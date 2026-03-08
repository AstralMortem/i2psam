from pydantic import BaseModel, IPvAnyAddress, Field
from i2psam.types import SigningKeyType


class SAMConfig(BaseModel):
    host: IPvAnyAddress = "127.0.0.1"
    port: int = 7656
    udp_port: int = 7655

    min_version: str = Field(default="3.0")
    max_version: str = Field(default="3.0")
    user: str | None = Field(default=None)
    password: str | None = Field(default=None)
    signature_type: SigningKeyType = Field(default=SigningKeyType.EDDSA_SHA512_ED25519)

    connection_timeout: int = 10
    connection_retries: int = 3
    exponential_backoff: bool = False
