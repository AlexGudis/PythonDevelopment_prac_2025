import cowsay
from io import StringIO
import asyncio
import time
import random


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
    """Class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.queue = asyncio.Queue()

    def move(self, d_x, d_y):
        self.x = (self.x + d_x) % 10
        self.y = (self.y + d_y) % 10
        return f"Moved to ({self.x}, {self.y})"


class Monster:
    """Class"""
    def __init__(self, x, y, hp, name, phrase=''):
        self.x = x
        self.y = y
        self.hp = hp
        self.phrase = phrase
        self.name = name

    def say_hi(self):
        if self.name == 'jgsbat':
            return cowsay.cowsay(self.phrase, cowfile=jgsbat)
        else:
            return cowsay.cowsay(self.phrase, cow=self.name)


class MUD:
    """Game class"""

    def __init__(self):
        self.pole = [['*' for _ in range(10)] for _ in range(10)]
        self.monsters_coords = set()
        self.weapons = {'sword': 10, 'spear': 15, 'axe': 20}

    def encounter(self, x, y):
        m = self.pole[y][x]
        if (x, y) in self.monsters_coords:
            return m.say_hi()
        return ''

    def moving(self, player, d_x, d_y):
        s = player.move(d_x, d_y)
        if (player.x, player.y) in self.monsters_coords:
            s += self.encounter(player.x, player.y)
        return s

    def do_addmon(self, x, y, hp, hello, name):
        mes = ''
        m = Monster(x, y, hp, name, hello)
        mes += f'Added monster {
            m.name} to ({
            m.x}, {
            m.y}) saying {
                m.phrase} with hp={
                    m.hp}'
        if (m.x, m.y) in self.monsters_coords:
            mes += "\nReplaced the old monster"
        self.monsters_coords.add((m.x, m.y))
        self.pole[m.y][m.x] = m
        return mes

    def do_attack(self, x, y, weapon, name):
        mes = ''
        m = self.pole[y][x]
        if m == '*' or m.name != name:  # монстра в принципе нет или нет с таким названием
            return f"No {name} here"
        else:
            damage = weapon
            if m.hp < damage:
                damage = m.hp

            m.hp -= damage
            mes += f'Attacked {m.name}, damage {damage} hp'

            if m.hp == 0:
                self.pole[y][x] = '*'
                self.monsters_coords.remove((x, y))
                mes += f'\n{m.name} died'
            else:
                self.pole[y][x] = m
                mes += f'\n{m.name} now has {m.hp}'
        return mes

    def generate_sayall(self, args):
        return ' '.join(args)


async def send_all(mes, exception=None):
    for out in players.values():
        print(out)
        if out != exception:
            # print('I have sent smth')
            await out.queue.put(f"{mes}")


async def echo(reader, writer):
    """Main loop"""
    global game, players

    send = asyncio.create_task(reader.readline())

    await asyncio.wait_for(send, timeout=None)
    login = send.result().decode()[:-1]
    if login in players:
        writer.write('0'.encode())
        writer.close()
        send.cancel()
        await writer.wait_closed()
        return
    else:
        players[login] = Gamer(0, 0)
        receive = asyncio.create_task(players[login].queue.get())
        writer.write(f"1".encode())
        await send_all(f'New player: {login}', exception=players[login])

    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(login, me)

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        print('Pipi papa popo')
        for request in done:
            if request is send:
                send = asyncio.create_task(reader.readline())
                match request.result().decode().split():
                    case ['addmon', *args]:
                        name, x, y, hp = args[:4]
                        hello = ' '.join(args[4:])
                        print('Sending result of addmon')
                        await send_all(f'User {login} did: {game.do_addmon(int(x), int(y), int(hp), hello, name)}', exception=players[login])

                    case ['move', *args]:
                        d_x, d_y = [int(i) for i in args]
                        writer.write(
                            game.moving(
                                players[login],
                                d_x,
                                d_y).encode())

                    case ['sayall', *args]:
                        print(f'I got {args}')
                        await send_all(f'{login}: {game.generate_sayall(args)}', exception=players[login])

                    case ['attack', *args]:
                        x, y = players[login].x, players[login].y
                        weapon, name = args
                        await send_all(f'{login} {game.do_attack(x, y, int(game.weapons[weapon]), name)}')

            if request is receive:
                receive = asyncio.create_task(players[login].queue.get())
                writer.write(f"{request.result()}\n".encode())
                await writer.drain()

    send.cancel()
    receive.cancel()
    writer.close()
    print(login, "LEFT")
    del players[login]
    send_all(f"{login} left")
    await writer.wait_closed()



async def monster_go():
    """Ramdom m move"""
    cnt = 0
    move_to = {'right':(1, 0), 'left':(-1, 0), 'up': (0, -1), 'down': (0, 1)}
    # left, right, up, down
    while True:
        cnt += 1
        await asyncio.sleep(30)
        #await send_all(f'BOOOO{cnt}')
        if game.monsters_coords:
            not_done = True
            random_m_x = -1
            random_m_y = -1
            while not_done:
                random_m_x, random_m_y = random.choice(list(game.monsters_coords))
                random_monstr = game.pole[random_m_y][random_m_x]
                print(random_monstr.say_hi())

                direction = random.choice(list(move_to.keys()))
                dx = move_to[direction][0]
                dy = move_to[direction][1]

                if (random_m_x + dx, random_m_y + dy) not in game.monsters_coords:
                    game.pole[random_m_y][random_m_x] = '*'
                    game.monsters_coords.remove((random_m_x, random_m_y))
                    random_m_x += dx
                    random_m_y += dy
                    random_monstr.x = random_m_x % 10
                    random_monstr.y = random_m_y % 10
                    game.pole[random_m_y][random_m_x] = random_monstr
                    not_done = False
                    game.monsters_coords.add((random_m_x, random_m_y))
                    await send_all(f'{random_monstr.name} moved one cell {direction}')
                    await send_all(f'{random_monstr.name} new coords is {random_monstr.x, random_monstr.y}')

            for p in players.values():
                if (p.x, p.y) == (random_m_x, random_m_y):
                    await p.queue.put(f"{game.encounter(random_m_x, random_m_y)}")

        

async def main():
    """Run it"""
    global game, players
    game = MUD()
    players = {}
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    asyncio.create_task(monster_go())
    async with server:
        await server.serve_forever()

asyncio.run(main())
