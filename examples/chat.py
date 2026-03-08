"""Example of peer-to-peer chat over i2p network by SAM protocol"""

import asyncio
import sys
from i2psam.client.connection import Connection
from i2psam.client import SAMClient
from i2psam.exceptions import SAMError


async def pump_stdin(writer: asyncio.StreamWriter) -> None:
    """
    Read lines from terminal stdin and send to peer.
    """
    loop = asyncio.get_running_loop()
    try:
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            if not line.endswith("\n"):
                line += "\n"
            writer.write(line.encode("utf-8"))
            await writer.drain()
    except asyncio.CancelledError:
        raise
    except Exception:
        # connection might be closed
        pass


async def pump_socket(reader: asyncio.StreamReader) -> None:
    """
    Read from peer and print to terminal.
    """
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            sys.stdout.write(data.decode("utf-8", errors="replace"))
            sys.stdout.flush()
    except asyncio.CancelledError:
        raise
    except Exception:
        pass


async def run_chat(conn: Connection) -> None:
    """
    Run bidirectional chat until either side closes.
    """
    t1 = asyncio.create_task(pump_stdin(conn.writer))
    t2 = asyncio.create_task(pump_socket(conn.reader))

    done, pending = await asyncio.wait({t1, t2}, return_when=asyncio.FIRST_COMPLETED)

    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)

    await conn.close()
    # try:
    #     conn.writer.close()
    #     await writer.wait_closed()
    # except Exception:
    #     pass


# --------------------------
# Listener / Connector modes
# --------------------------


async def listen_mode():
    sam = SAMClient()

    keys = await sam.dest_generate()
    print("\n=== SHARE THIS DESTINATION WITH THE OTHER TERMINAL ===")
    # The peer should connect to your PUBLIC destination, not your private key.
    # DEST GENERATE returns PUB and PRIV.
    print(keys.pub)
    print("====================================================\n")
    print("Waiting for inbound STREAM connection... (Ctrl+C to stop)\n")

    async with sam.session("chat-listen", destination=keys.priv) as sess:
        while True:
            try:
                async with sess.accept_stream() as (peer_dest, stream):
                    print(f"\n[Connected] peer={peer_dest or 'unknown'}")
                    await run_chat(stream)
            except SAMError as e:
                print(f"[sam error] {e}")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"[ERROR] {e}")


async def connect_mode(dest: str):
    sam = SAMClient()

    async with sam.session("chat-connect", destination="TRANSIENT") as sess:
        try:
            async with sess.connect_stream(dest) as stream:
                print("[connected] Type messages and press Enter.\n")
                await run_chat(stream)
                print("\n[disconnected]")
        except SAMError as e:
            print(f"[sam error] {e}")


def usage():
    print(
        "Usage:\n"
        "  python chat.py listen\n"
        "  python chat.py connect <DESTINATION>\n\n"
        "Steps:\n"
        "  1) Terminal A: python chat.py listen\n"
        "  2) Copy the printed destination\n"
        "  3) Terminal B: python chat.py connect <PASTED_DEST>\n"
    )


async def main():
    if len(sys.argv) < 2:
        usage()
        return
    mode = sys.argv[1].lower()

    if mode == "listen":
        await listen_mode()
    elif mode == "connect":
        if len(sys.argv) < 3:
            usage()
            return
        await connect_mode(sys.argv[2])
    else:
        usage()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
