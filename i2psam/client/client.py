from typing import Literal
from i2psam.types import SessionStyle
from .config import SAMConfig
from .connection import Connection
from i2psam.commands.base import I2PCommand, R
from i2psam.exceptions import SAMClientError
from i2psam.logs import get_logger
from contextlib import asynccontextmanager
import asyncio

logger = get_logger("client")


class SAMClient:
    def __init__(self, config: SAMConfig = SAMConfig()):
        self.cfg = config

    async def _connect(self):
        logger.debug("Connecting to SAM bridge at %s:%s", self.cfg.host, self.cfg.port)
        try:
            rx, tx = await asyncio.wait_for(
                asyncio.open_connection(self.cfg.host, self.cfg.port),
                timeout=self.cfg.connection_timeout,
            )
            logger.debug("Connected to SAM bridge")
            return Connection(client=self, reader=rx, writer=tx)
        except (asyncio.TimeoutError, OSError) as e:
            logger.warning("Connection to SAM bridge failed: %s", e)
            raise SAMClientError(
                f"Unable to connect to {self.cfg.host}:{self.cfg.port}. {e}"
            ) from e

    @asynccontextmanager
    async def connection(self, autohandshake: bool = True):
        last_error = None
        for attempt in range(self.cfg.connection_retries + 1):
            try:
                logger.debug("Connection attempt %s", attempt + 1)
                conn = await self._connect()
                if autohandshake:
                    logger.debug("Performing HELLO handshake")
                    await conn.handshake()
                try:
                    yield conn
                finally:
                    await conn.close()
                return
            except SAMClientError as e:
                last_error = e

                if attempt >= self.cfg.connection_retries:
                    break

                if self.cfg.exponential_backoff:
                    delay = self.cfg.connection_timeout * (2**attempt)
                    logger.debug("Retrying after backoff delay=%ss", delay)
                    await asyncio.sleep(delay)
        logger.error(
            "Failed to connect after %s attempts",
            self.cfg.connection_retries + 1,
        )
        raise SAMClientError(
            f"Failed to connect after {self.cfg.connection_retries + 1} attempts"
        ) from last_error

    @asynccontextmanager
    async def session(
        self,
        session_id: str,
        destination: str | Literal["TRANSIENT"],
        style: SessionStyle = SessionStyle.STREAM,
        **kw,
    ):
        async with self.connection() as conn:
            session = await conn.create_session(session_id, destination, style, **kw)
            yield session

    async def request(self, msg: I2PCommand[R], *, autohandshake: bool = True) -> R:
        async with self.connection(autohandshake) as conn:
            return await conn.request(msg)

    async def raw_request(self, msg: str | bytes, *, autohandshake: bool = True) -> str:
        async with self.connection(autohandshake) as conn:
            return await conn.raw_request(msg)

    async def dest_generate(self, *, autohandshake: bool = True, **kw):
        async with self.connection(autohandshake) as conn:
            return await conn.dest_generate(**kw)

    async def naming_lookup(self, name: str, *, autohandshake: bool = True, **kw):
        async with self.connection(autohandshake) as conn:
            return await conn.naming_lookup(name, **kw)
