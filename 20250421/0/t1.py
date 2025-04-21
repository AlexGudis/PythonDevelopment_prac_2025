import asyncio
from kv import sqroots

async def echo(reader, writer):
    while data := await reader.readline():
        res = data.strip().decode()
        try:
            ans = sqroots(res)
        except Exception:
            raise ValueError
        
        writer.write(f"{ans}\n".encode())
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


def serve():
    asyncio.run(main())