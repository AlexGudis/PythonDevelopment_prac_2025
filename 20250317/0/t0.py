import asyncio
import shlex

async def echo(reader, writer):
    while data := await reader.readline():
        data = data.decode('utf-8')
        check = shlex.split(data)
        if check[0] == 'print':
            data = data[6:].encode('utf-8')
            writer.write(data.swapcase())
        elif check[0] == 'info':
            me = "{}:{}".format(*writer.get_extra_info('peername'))
            me = me.split(':')
            if check[1] == 'host':
                writer.write(me[0].encode() + b'\n')
            elif check[1] == 'port':
                writer.write(me[1].encode() + b'\n')
            else:
                print('invalid argument')
        else:
            print('invalid argument')
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())