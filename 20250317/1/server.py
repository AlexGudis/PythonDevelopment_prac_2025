import cowsay
import sys
from io import StringIO
import shlex
import readline
import cmd
import asyncio


class Gamer:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, d_x, d_y):
        self.x = (self.x + d_x) % 10
        self.y = (self.y + d_y) % 10
        return f"{self.x} {self.y}"

class Monster:
    def __init__(self, x, y, hp, name, phrase=''):
        self.x = x
        self.y = y
        self.hp = hp
        self.phrase = phrase
        self.name = name

class MUD:

    def __init__(self):
        self.pole = [['*' for _ in range(10)] for _ in range(10)]
        self.monsters_coords = set()
        self.weapons = {'sword':10, 'spear':15, 'axe':20}

    def encounter(self, x, y):
        if (x,y) in self.monsters_coords:
            return f' {self.pole[y][x].name} {self.pole[y][x].phrase}'
        return ''

    def moving(self, player, d_x, d_y):
        s = player.move(d_x, d_y)
        if (player.x, player.y) in self.monsters_coords:
            s += self.encounter(player.x, player.y)
        #print(s)
        return s

    def do_addmon(self, x, y, hp, hello, name):
        repl = '0'
        m = Monster(x, y, hp, name, hello)
        #print(f'Created monster with {hello} phrase')
        if (m.x,m.y) in self.monsters_coords:
            repl = '1'
        self.monsters_coords.add((m.x, m.y))
        self.pole[m.y][m.x] = m 
        return repl

    def do_attack(self, x, y, weapon, name):

        m = self.pole[y][x]
        if m == '*' or m.name != name: # монстра в принципе нет или нет с таким названием
            return 'no'

        else:
            damage = self.weapons[weapon]
            if m.hp < damage:
                damage = m.hp

            m.hp -= damage

            if m.hp == 0:
                self.pole[y][x] = '*'
                self.monsters_coords.remove((x, y))
                return f'{damage} 0'
            else:
                self.pole[y][x] = m
                return f'{damage} {m.hp}'


async def echo(reader, writer):
    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(me)
    game = MUD()
    player = Gamer(0, 0)

    queue = asyncio.Queue()
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(queue.get())

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for request in done:
            if request is send:
                send = asyncio.create_task(reader.readline())
                match request.result().decode().split():
                    case ['addmon', *args]:
                        name, x, y, hp = args[:4]
                        hello = ' '.join(args[4:])
                        writer.write(game.do_addmon(int(x), int(y), int(hp), hello, name).encode())
                    case ['attack', *args]:
                        x, y = player.x, player.y
                        weapon, name = args
                        writer.write(game.do_attack(x, y, weapon, name).encode())
                    case ['move', *args]:
                        d_x, d_y = [int(i) for i in args]
                        writer.write(game.moving(player, d_x, d_y).encode())

    send.cancel()
    receive.cancel()
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 2228)
    async with server:
        await server.serve_forever()

asyncio.run(main())


