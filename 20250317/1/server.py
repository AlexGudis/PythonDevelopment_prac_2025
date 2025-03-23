import cowsay
import sys
from io import StringIO
import shlex
import readline
import cmd
import asyncio



jgsbat = cowsay.read_dot_cow(StringIO(r"""
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\'--'//__
         (((""`  `"")))
"""))


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

    def say_hi(self):
        if self.name == 'jgsbat':
            print(cowsay.cowsay(self.phrase, cowfile=jgsbat))
        else:
            print(cowsay.cowsay(self.phrase, cow=self.name))

class MUD(cmd.Cmd):
    prompt = "Input cmd>> "

    def __init__(self, completekey = "tab", stdin = None, stdout = None):
        super().__init__(completekey, stdin, stdout)
        self.pole = [['*' for _ in range(10)] for _ in range(10)]
        self.monsters_coords = set()
        self.g = Gamer(0,0)
        self.weapons = {'sword':10, 'spear':15, 'axe':20}

    def encounter(self, x, y):
        if (x,y) in self.monsters_coords:
            return f' {self.pole[y][x].name} {self.pole[y][x].phrase}'
        return ''

    def moving(self, player, d_x, d_y):
        s = player.move(d_x, d_y)
        if (player.x, player.y) in self.monsters_coords:
            s += self.encounter(player.x, player.y)
        print(s)
        return s

    def do_addmon(self, x, y, hp, hello, name):
        repl = '0'
        m = Monster(x, y, hp, name, hello)
        print(f'Created monster with {hello} phrase')
        if (m.x,m.y) in self.monsters_coords:
            repl = '1'
        self.monsters_coords.add((m.x, m.y))
        self.pole[m.y][m.x] = m 
        return repl

    def check_pos(self):
        if (self.g.x,self.g.y) in self.monsters_coords:
            self.encounter(self.g.x, self.g.y)

    def do_attack(self, args):
        if len(args) == 0:
            print('Invalid input. You should provide at least name of the monster to attack')
            return

        available_weapons = [k for k,v in self.weapons.items()]
        weapon = 'sword'
        args = shlex.split(args)
        if 'with' in args: # Мы передали на вход какое-то оружие
            weapon = args[-1]
        if weapon not in available_weapons:
            print('Unknown weapon')
            return
    
        x = self.g.x
        y = self.g.y

        m = self.pole[y][x]
        if m == '*' or m.name != args[0]: # монстра в принципе нет или нет с таким названием
            print(f'No {args[0]} here')
        else:
            damage = self.weapons[weapon]
            if m.hp < damage:
                damage = m.hp

            m.hp -= damage
            print(f'Attacked {m.name}, damage {damage} hp')

            if m.hp == 0:
                print(f'{m.name} died')
                self.pole[y][x] = '*'
                self.monsters_coords.remove((x, y))
            else:
                print(f'{m.name} now has {m.hp}')
                self.pole[y][x] = m


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
                        #print(f'Server gets args with addmon command: name = {name}, x = {x}, y = {y}, hp = {hp}, hello = {hello}')
                        writer.write(game.do_addmon(int(x), int(y), int(hp), hello, name).encode())
                    case ['attack', *args]:
                        x, y = player.x, player.y
                        weapon, name = args
                        writer.write(game.attack(x, y, int(weapon), name).encode())
                    case ['move', *args]:
                        d_x, d_y = [int(i) for i in args]
                        writer.write(game.moving(player, d_x, d_y).encode())
            if request is receive:
                receive = asyncio.create_task(my_queue.get())

    send.cancel()
    receive.cancel()
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())


