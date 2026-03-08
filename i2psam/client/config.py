from pydantic import BaseModel, IPvAnyAddress


class SAMConfig(BaseModel):
    host: IPvAnyAddress = "127.0.0.1"
    port: int = 7656
    udp_port: int = 7655

    connection_timeout: int = 10
    connection_retries: int = 3
    exponential_backoff: bool = False
