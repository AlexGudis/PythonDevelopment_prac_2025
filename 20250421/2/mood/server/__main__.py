"""
Multi User Dungeon (MUD) Game Server
------------------------------------
A multiplayer game where players can move around a grid, encounter monsters, cooperate, and interact with them.

Modules used:
- `cowsay`: For fancy monster greetings.
- `asyncio`: Asynchronous event-driven communication between server and players.
- `random`, `time`: For random monster behavior and timing.
- `common.jgsbat`: Custom cowsay figure for the monster 'jgsbat'.

Project Components:
- `Gamer`: Player model.
- `Monster`: Monster model.
- `MUD`: Game field and logic manager.
- Asynchronous server functions for player interaction and monster actions.
"""


import cowsay
import asyncio
import time
import random
from ..common import jgsbat

movemonsters = True



# ================================
# Player Class
# ================================


class Gamer:

    """Represents a player in the MUD game.
    
    Attributes:
        x (int): Current X-coordinate on the game field (0-9).
        y (int): Current Y-coordinate on the game field (0-9).
        queue (asyncio.Queue): Message queue for asynchronous communication.
    """

    def __init__(self, x, y):

        """Initialize the player with starting coordinates.
        Default position is (0,0) for each palyer
        
        Args:
            x: Initial X position (0-9).
            y: Initial Y position (0-9).
        """

        self.x = x
        self.y = y
        self.queue = asyncio.Queue()

    def move(self, d_x, d_y):

        """Move the player by specified deltas with wrap-around.
        
        Args:
            d_x: Movement delta on X-axis (+/- 1).
            d_y: Movement delta on Y-axis (+/- 1).
            Depends on the specific move commands. See client docs
            
        Returns:
            String confirmation with new coordinates of the player.
            
        Example:
            >>> right
            'Moved to (1, 0)'
        """

        self.x = (self.x + d_x) % 10
        self.y = (self.y + d_y) % 10
        return f"Moved to ({self.x}, {self.y})"


# ================================
# Monster Class
# ================================

class Monster:
    
    """Represents a game monster with interactive abilities.
    
    Attributes:
        x (int): X-coordinate on the game field.
        y (int): Y-coordinate on the game field.
        hp (int): Hit points of the monster.
        name (str): Unique identifier (e.g. 'dragon', 'jgsbat').
        phrase (str): Greeting message when encountered.
    """

    def __init__(self, x, y, hp, name, phrase=''):
        self.x = x
        self.y = y
        self.hp = hp
        self.phrase = phrase
        self.name = name

    def say_hi(self):

        """
        Return a cowsay greeting from the monster.

        Returns:
            str: Monster's greeting as ASCII art.
        """

        if self.name == 'jgsbat':
            return cowsay.cowsay(self.phrase, cowfile=jgsbat)
        else:
            return cowsay.cowsay(self.phrase, cow=self.name)



# ================================
# MUD Game Class
# ================================

class MUD:
    """
    Core game logic handler.
    """

    def __init__(self):
        """
        Initialize the game field, monster tracking, and weapon data.
        """

        self.pole = [['*' for _ in range(10)] for _ in range(10)]
        self.monsters_coords = set()
        self.weapons = {'sword': 10, 'spear': 15, 'axe': 20}

    def encounter(self, x, y):
        """
        Check if a player encounters a monster.

        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.

        Returns:
            str: Monster greeting or empty string if no monster found here.
        """

        m = self.pole[y][x]
        if (x, y) in self.monsters_coords:
            return m.say_hi()
        return ''

    def moving(self, player, d_x, d_y):
        """
        Move a player and handle encounters.

        Args:
            player (Gamer): The player object.
            d_x (int): Delta X movement.
            d_y (int): Delta Y movement.

        Returns:
            str: Move result and potential encounter message.
        """

        s = player.move(d_x, d_y)
        if (player.x, player.y) in self.monsters_coords:
            s += self.encounter(player.x, player.y)
        return s

    def do_addmon(self, x, y, hp, hello, name):
        """
        Add or replace a monster at a given position.

        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.
            hp (int): Monster's HP.
            hello (str): Monster's greeting.
            name (str): Monster type.

        Returns:
            str: Result message.
        """

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
        """
        Handle an attack action from a player.

        Args:
            x (int): Player's X-coordinate.
            y (int): Player's Y-coordinate.
            weapon_damage (int): Weapon's damage points.
            name (str): Name of the targeted monster.

        Returns:
            str: Result of the attack.
        """

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
        """
        Generate a broadcast message from a player.

        Args:
            args (list): List of words.

        Returns:
            str: Combined message string.
        """

        return ' '.join(args)
    
    def do_movemonsters(self, args):
        global movemonsters

        if args == 'on':
            movemonsters = True
            return 'Moving monsters: on'
        else:
            movemonsters = False
            return 'Moving monsters: off'
        
    #def set_locale(self, player, loc):
    #    pass



# ================================
# Async Functions
# ================================

async def send_all(mes, exception=None):
    """
    Send a message to all players except optionally one.

    Args:
        message (str): The message to send.
        exception (Gamer, optional): Player to exclude.
    """

    for out in players.values():
        print(out)
        if out != exception:
            # print('I have sent smth')
            await out.queue.put(f"{mes}")


async def echo(reader, writer):
    """
    Main player communication loop.

    Args:
        reader (asyncio.StreamReader): Player input stream.
        writer (asyncio.StreamWriter): Player output stream.
    """

    global game, players
    local = 'en_US.UTF-8'

    send = asyncio.create_task(reader.readline())

    await asyncio.wait_for(send, timeout=None)
    login = send.result().decode()[:-1]

    # Check if player is really a new one
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
                    
                    case ['movemonsters', type]:
                        #print('WANT TO', type)
                        await send_all(f'{game.do_movemonsters(type)}')

                    case ['locale', loc]:
                        local = loc
                        writer.write(f"Set up locale: {local}")

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
    """
    Periodically move monsters randomly.
    """

    cnt = 0
    move_to = {'right':(1, 0), 'left':(-1, 0), 'up': (0, -1), 'down': (0, 1)}
    # left, right, up, down
    while True:
        cnt += 1
        await asyncio.sleep(30)
        if game.monsters_coords and movemonsters:
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

                if ( (random_m_x + dx) % 10, (random_m_y + dy) % 10) not in game.monsters_coords:
                    game.pole[random_m_y][random_m_x] = '*'
                    game.monsters_coords.remove((random_m_x, random_m_y))
                    random_m_x += dx
                    random_m_y += dy
                    random_monstr.x = random_m_x % 10
                    random_monstr.y = random_m_y % 10
                    game.pole[random_monstr.y][random_monstr.x] = random_monstr
                    not_done = False
                    game.monsters_coords.add((random_monstr.x, random_monstr.y))
                    await send_all(f'{random_monstr.name} moved one cell {direction}')
                    await send_all(f'{random_monstr.name} new coords is {random_monstr.x, random_monstr.y}')

            for p in players.values():
                if (p.x, p.y) == (random_m_x, random_m_y):
                    await p.queue.put(f"{game.encounter(random_m_x, random_m_y)}")

        

async def main():
    """
    Entry point to start the game server.
    """

    
    global game, players
    game = MUD()
    players = {}
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    asyncio.create_task(monster_go())
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
