# i2psam

Async Python client for the I2P SAM (Simple Anonymous Messaging) protocol.

`i2psam` provides:
- connection management with retry/backoff
- SAM handshake, session creation, and command helpers
- stream connect/accept/forward helpers
- datagram send/receive helpers
- optional package logging

## Requirements

- Python `>=3.10`
- Running I2P router with SAM enabled
  - default SAM TCP port: `7656`
  - default SAM UDP port: `7655`

## Installation

From pip
```bash
pip install i2psam
```

For UV
```bash
uv add i2psam
```

From source:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

## Quick Start

```python
import asyncio
from i2psam import SAMClient


async def main():
    sam = SAMClient()

    # Ask SAM bridge to generate destination keys
    keys = await sam.dest_generate()
    print("Public destination:", keys.pub)

    # Create STREAM session
    async with sam.session("my-session", destination=keys.priv) as sess:
        print("Session created:", sess.session_id)


asyncio.run(main())
```

## Configuration

```python
from i2psam import SAMClient, SAMConfig

cfg = SAMConfig(
    host="127.0.0.1",
    port=7656,
    udp_port=7655,
    connection_timeout=10,
    connection_retries=3,
    exponential_backoff=False,
)

sam = SAMClient(cfg)
```

## STREAM Example

### Accept inbound connection

```python
async with sam.session("listener", destination=keys.priv) as sess:
    async with sess.accept_stream() as (peer_dest, conn):
        data = await conn.read_line()
        print("from", peer_dest, data)
```

### Connect to peer

```python
peer_dest = "<peer public destination>"

async with sam.session("dialer", destination="TRANSIENT") as sess:
    async with sess.connect_stream(peer_dest) as conn:
        await conn.write("hello from i2psam")
```

Full chat example: [examples/chat.py](examples/chat.py)

## DATAGRAM Example

```python
async with sam.session("dgram", destination=keys.priv) as sess:
    async with sess.create_datagram() as dg:
        dg.sendto("<peer destination>", b"ping")
        sender, payload = await dg.recv()
        print(sender, payload)
```

## Low-level Command API

You can send command models directly:

```python
from i2psam import SAMClient
from i2psam.commands.commands import HelloVersion

reply = await SAMClient().request(HelloVersion(MIN="3.0", MAX="3.3"))
print(reply.version)
```

Or send raw SAM lines:

```python
raw = await SAMClient().raw_request("HELLO VERSION MIN=3.0 MAX=3.3")
print(raw)
```

## Logging

Library logging is silent by default (`NullHandler`).

Enable logs:

```python
from i2psam import configure_logging

configure_logging("DEBUG")
```

Create named logger if needed:

```python
from i2psam import get_logger

log = get_logger("custom")
log.info("hello")
```

## Errors

Common exceptions:
- `SAMError`
- `SAMClientError`
- `SAMSessionError`
- `SAMStreamError`
- `SAMDatagramError`

Use them to handle bridge/network/protocol failures.

## Running Tests

```bash
pytest -q
```

