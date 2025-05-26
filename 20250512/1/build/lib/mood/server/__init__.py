"""Multi User Dungeon (MUD) Game Server

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
import gettext
import asyncio
import random
import locale
import os
from ..common import jgsbat

movemonsters = True


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
        """Monster parameters"""

        self.x = x
        self.y = y
        self.hp = hp
        self.phrase = phrase
        self.name = name

    def say_hi(self):
        """Return a cowsay greeting from the monster.

        Returns:
            str: Monster's greeting as ASCII art.
        """

        if self.name == 'jgsbat':
            return cowsay.cowsay(self.phrase, cowfile=jgsbat)
        else:
            return cowsay.cowsay(self.phrase, cow=self.name)


localedir = os.path.join(os.path.dirname(__file__), "locales")

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("messages", localedir, ["ru"]),
    ("en_US", "UTF-8"): gettext.NullTranslations()
}
locale.setlocale(locale.LC_CTYPE, locale.getdefaultlocale())


def _(text):
    return LOCALES[locale.getlocale()].gettext(text)


print(_('Heloo!!!'))


# ================================
# Gamer Class
# ================================


class Gamer:
    """Represents a player in the MUD game.

    Attributes:
        x (int): Current X-coordinate on the game field (0-9).
        y (int): Current Y-coordinate on the game field (0-9).
        queue (asyncio.Queue): Message queue for asynchronous communication.
    """

    def __init__(self, x, y, lang=('en_US', 'UTF-8')):
        """Initialize the player with starting coordinates.
        Default position is (0,0) for each palyer

        Args:
            x: Initial X position (0-9).
            y: Initial Y position (0-9).
        """

        self.translate = lang
        self.x = x
        self.y = y
        self.queue = asyncio.Queue()

    def config_language(self, args):
        """Choose locale"""

        if args == 'ru_RU.UTF8':
            # print('Поставили русскую локаль')
            self.translate = ('ru_RU', 'UTF-8')
        else:
            self.translate = ('en_US', 'UTF-8')

        locale.setlocale(locale.LC_ALL, self.translate)
        return _("Set up locale: {args}").format(args=args)

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
        print(f'Locale = {self.translate}')
        locale.setlocale(locale.LC_ALL, self.translate)
        return _("Moved to ({x}, {y})\n").format(x=self.x, y=self.y)


def generate_translation(fun=None, name='', x=0, y=0, hello='', login='', damage=0, check=0, hp=0):
    """Used to generete msg to help localize messaging"""
    if fun == 'addmon':
        replaced = '' if check == 0 else _("Replaced the old monster\n")
        return _("Added monster {name} to ({x}, {y}) saying {hello}\n{replaced}").format(name=name, x=x, y=y, hello=hello, replaced=replaced)
    elif fun == 'attack':
        if check == 0:
            health = _("{name} died\n").format(name=name)
        else:
            health = (_("{name} now has").format(name=name) + LOCALES[locale.getlocale(
            )].ngettext(" {hp} hit point\n", " {hp} hit points\n", hp).format(hp=hp))
        return (_("{login} attacked {name}").format(login=login, name=name) + LOCALES[locale.getlocale()].ngettext(", damage {damage} hit point\n", ", damage {damage} hit points\n", damage).format(damage=damage) + health)
    elif fun == 'new':
        return _('New player: {login}').format(login=login)
    else:
        return _("{login} left").format(login=login)


# ================================
# MUD Game Class
# ================================

class MUD:
    """Core game logic handler."""

    def __init__(self):
        """Initialize the game field, monster tracking, and weapon data."""

        self.pole = [['*' for _ in range(10)] for _ in range(10)]
        self.monsters_coords = set()
        self.weapons = {'sword': 10, 'spear': 15, 'axe': 20}

    def encounter(self, x, y):
        """Check if a player encounters a monster.

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
        """Move a player and handle encounters.

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
        """Add or replace a monster at a given position.

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

        params = {'name': name, 'x': x, 'y': y, 'hello': hello}
        if (m.x, m.y) in self.monsters_coords:
            mes += "\nReplaced the old monster"
            params['check'] = 1
        else:
            params['check'] = 0
        self.monsters_coords.add((m.x, m.y))
        self.pole[m.y][m.x] = m
        return params

    def do_attack(self, x, y, weapon, name):
        """Handle an attack action from a player.

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
            params = {'name': m.name, 'damage': damage}

            if m.hp == 0:
                self.pole[y][x] = '*'
                self.monsters_coords.remove((x, y))
                mes += f'\n{m.name} died'
                params['check'] = 0
            else:
                self.pole[y][x] = m
                mes += f'\n{m.name} now has {m.hp}'
                params['check'] = 1
                params['hp'] = m.hp
        return params

    def generate_sayall(self, args):
        """Generate a broadcast message from a player.

        Args:
            args (list): List of words.

        Returns:
            str: Combined message string.
        """

        return ' '.join(args)

    def do_movemonsters(self, args, player):
        """On/off monster movements"""

        global movemonsters
        locale.setlocale(locale.LC_ALL, player.translate)

        if args == 'on':
            movemonsters = True
            return _('Moving monsters: on')
        else:
            movemonsters = False
            return _('Moving monsters: off')


# ================================
# Async Functions
# ================================

async def echo(reader, writer):
    """Main player communication loop.

    Args:
        reader (asyncio.StreamReader): Player input stream.
        writer (asyncio.StreamWriter): Player output stream.
    """

    global game, players

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
        await broadcast_message(message_generator='new', generator_args={'login': login}, exclude_player=players[login])

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
                        await broadcast_message(message_generator='addmon', generator_args=game.do_addmon(int(x), int(y), int(hp), hello, name))

                    case ['move', *args]:
                        default_loc = locale.getlocale()
                        d_x, d_y = [int(i) for i in args]
                        writer.write(game.moving(
                            players[login], d_x, d_y).encode())
                        locale.setlocale(locale.LC_ALL, default_loc)

                    case ['sayall', *args]:
                        print(f'I got {args}')
                        await broadcast_message(f'{login}: {game.generate_sayall(args)}', exclude_player=players[login])

                    case ['attack', *args]:
                        x, y = players[login].x, players[login].y
                        weapon, name = args
                        answer = game.do_attack(
                            x, y, int(game.weapons[weapon]), name)
                        answer['login'] = login
                        await broadcast_message(message_generator='attack', generator_args=answer)

                    case ['movemonsters', type]:
                        # print('WANT TO', type)
                        default_loc = locale.getlocale()
                        writer.write(game.do_movemonsters(
                            type, players[login]).encode())
                        locale.setlocale(locale.LC_ALL, default_loc)

                    case ['locale', loc]:
                        writer.write(
                            players[login].config_language(loc).encode())

            if request is receive:
                receive = asyncio.create_task(players[login].queue.get())
                writer.write(f"{request.result()}\n".encode())
                await writer.drain()

    send.cancel()
    receive.cancel()
    writer.close()
    print(login, "LEFT")
    del players[login]
    await broadcast_message(message_generator='left', generator_args={'login': login})
    await writer.wait_closed()


async def monster_go():
    """Periodically moves monsters on the game field in random directions with localization support.

    This coroutine runs indefinitely in the background, performing the following actions every 30 seconds:
    1. Selects a random monster from the current monsters on the field
    2. Chooses a random direction (left, right, up, down)
    3. Validates the move (ensuring no collision with other monsters)
    4. Updates the monster's position on the game field
    5. Notifies all players about the movement in their respective languages
    6. Handles player encounters if they occupy the same cell as the monster

    Example Usage:
    >>> movemonsters off
    >>> movemonsters on

    Note:
    - The function runs indefinitely until the main program terminates
    - Movement can be globally disabled via the 'movemonsters' flag
    - Actual movement interval is fixed at 30 seconds
    """

    cnt = 0
    move_to = {_('right'): (1, 0), _('left'): (-1, 0),
               _('up'): (0, -1), _('down'): (0, 1)}

    directions = {
        'en_US': {'right': (1, 0), 'left': (-1, 0), 'up': (0, -1), 'down': (0, 1)},
        'ru_RU': {'right': (1, 0), 'left': (-1, 0), 'up': (0, -1), 'down': (0, 1)}
    }

    direction_names = {
        'en_US': {
            (1, 0): 'right',
            (-1, 0): 'left',
            (0, -1): 'up',
            (0, 1): 'down'
        },
        'ru_RU': {
            (1, 0): 'вправо',
            (-1, 0): 'влево',
            (0, -1): 'вверх',
            (0, 1): 'вниз'
        }
    }

    # left, right, up, down
    while True:
        cnt += 1
        await asyncio.sleep(30)
        if game.monsters_coords and movemonsters:
            not_done = True
            random_m_x = -1
            random_m_y = -1
            while not_done:
                random_m_x, random_m_y = random.choice(
                    list(game.monsters_coords))
                random_monstr = game.pole[random_m_y][random_m_x]
                print(random_monstr.say_hi())

                direction = random.choice(list(move_to.keys()))
                dx = move_to[direction][0]
                dy = move_to[direction][1]

                if ((random_m_x + dx) % 10, (random_m_y + dy) % 10) not in game.monsters_coords:
                    game.pole[random_m_y][random_m_x] = '*'
                    game.monsters_coords.remove((random_m_x, random_m_y))
                    random_m_x += dx
                    random_m_y += dy
                    random_monstr.x = random_m_x % 10
                    random_monstr.y = random_m_y % 10
                    game.pole[random_monstr.y][random_monstr.x] = random_monstr
                    not_done = False
                    game.monsters_coords.add(
                        (random_monstr.x, random_monstr.y))

                    for player in players.values():
                        locale.setlocale(locale.LC_ALL, player.translate)
                        lang = player.translate[0]  # 'en_US' или 'ru_RU'
                        direction = direction_names[lang][(dx, dy)]

                        await player.queue.put(_("{name} moved one cell {direction}").format(
                            name=random_monstr.name, direction=direction))

                        await player.queue.put(_("{name} new coords is {x}, {y}").format(
                            name=random_monstr.name, x=random_monstr.x, y=random_monstr.y))

            for p in players.values():
                if (p.x, p.y) == (random_m_x, random_m_y):
                    await p.queue.put(f"{game.encounter(random_m_x, random_m_y)}")


async def broadcast_message(
    message_text: str = '',
    message_generator: str = None,
    generator_args: dict = None,
    exclude_player: object = None
) -> None:
    """Sends a message to all connected players with localization support.

    Parameters:
        message_text (str): Base message text to send (if no generator provided)
        message_generator (str): Optional function to which we should provide args
        generator_args (dict): Arguments to use in the message generator
        exclude_player (Player): Specific player to exclude from receiving the message

    The function handles locale settings for each player individually and
    restores the original locale after completion.
    """
    if generator_args is None:
        generator_args = {}

    original_locale = locale.getlocale()

    try:
        for player in players.values():
            # Не отправляем сообщения самому себе
            if player == exclude_player:
                continue

            locale.setlocale(locale.LC_ALL, player.translate)

            final_message = (
                generate_translation(fun=message_generator, **generator_args)
                if message_generator else message_text
            )

            await player.queue.put(f"{final_message}")

    finally:
        locale.setlocale(locale.LC_ALL, original_locale)


async def main():
    """Main entry point for the MUD (Multi-User Dungeon) game server."""

    global game, players
    game = MUD()
    players = {}
    server = await asyncio.start_server(
        echo,
        '0.0.0.0',
        1337,        # Порт по умолчанию
    )
    asyncio.create_task(monster_go())

    async with server:
        await server.serve_forever()


def run_server():
    """Used to run the server"""

    asyncio.run(main())
