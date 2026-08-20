import asyncio
import sys

TARGET_HOST = "192.168.11.86"
TARGET_PORT = 8005
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8005

async def forward_stream(reader, writer):
    try:
        remote_reader, remote_writer = await asyncio.open_connection(TARGET_HOST, TARGET_PORT)
    except Exception as e:
        print(f"[Proxy] Connection to target {TARGET_HOST}:{TARGET_PORT} failed: {e}", flush=True)
        writer.close()
        return

    async def pipe(r, w):
        try:
            while True:
                data = await r.read(65536)
                if not data:
                    break
                w.write(data)
                await w.drain()
        except Exception:
            pass
        finally:
            try:
                w.close()
                await w.wait_closed()
            except Exception:
                pass

    await asyncio.gather(pipe(reader, remote_writer), pipe(remote_reader, writer))

async def main():
    server = await asyncio.start_server(forward_stream, LISTEN_HOST, LISTEN_PORT)
    print(f"[Proxy] Listening on {LISTEN_HOST}:{LISTEN_PORT} -> forwarding to {TARGET_HOST}:{TARGET_PORT}", flush=True)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
