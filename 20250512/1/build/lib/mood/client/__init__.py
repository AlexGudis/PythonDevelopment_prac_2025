"""Init for client"""

import cowsay
import shlex
import readline
import cmd
import os
import gettext
import locale
import webbrowser
from pathlib import Path

localedir = os.path.join(os.path.dirname(__file__), "locales")

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("messages", localedir, ["ru"]),
    ("en_US", "UTF-8"): gettext.NullTranslations()
}
locale.setlocale(locale.LC_CTYPE, locale.getdefaultlocale())

gamer_loca = ("en_US", "UTF-8")


def _(text):
    return LOCALES[locale.getlocale()].gettext(text)


class Client(cmd.Cmd):
    """Client functionality"""

    prompt = 'MUD> '
    intro = _("<<< Welcome to Python-MUD 0.1 >>>")

    readline.set_completer_delims(
        readline.get_completer_delims().replace('-', ''))

    def __init__(self, *args, socket, **kwargs):
        """Client basic parametrs"""

        self.s = socket
        return super().__init__(*args, **kwargs)
    
    def do_documentation(self, args):
        """Open documentation in browser"""
        print(f"{str(Path(__file__).parents[1])}")
        webbrowser.open(f"{str(Path(__file__).parents[1])}/../docs/build/html/index.html")

    def addmon_params_check(self, args):
        """Check params before adding monster"""

        args = shlex.split(args)
        args.insert(0, 'addmon')
        params = {'name': 'default', 'hello': 'Uwu', 'hp': 1, 'coords': (0, 0)}
        # params['name'] = args[args.index('addmon') + 1]

        # print(cowz)
        try:
            if args[args.index('addmon') + 1] in cowsay.list_cows() + ['jgsbat']:
                params['name'] = args[args.index('addmon') + 1]
            else:
                raise ValueError
        except ValueError:
            print(
                _('Incorrect name of the monster. It does not exists'))
            raise ValueError

        try:
            params['hello'] = args[args.index('hello') + 1]
        except ValueError:
            print(
                _('Something wrong with hello string when trying to parse it to a monster'))
            raise ValueError

        try:
            params['hp'] = int(args[args.index('hp') + 1])
            if params['hp'] <= 0:
                raise ValueError
        except ValueError:
            print(_('hp argument should be a positive integer'))
            raise ValueError

        try:
            start = args.index('coords')
            params['coords'] = (int(args[start + 1]), int(args[start + 2]))
        except ValueError:
            print(_('Something wrong with coords when trying to parse it to a monster'))
            raise ValueError

        return params['coords'][0], params['coords'][1], params['hp'], params['hello'], params['name']

    def do_addmon(self, args):
        """Adds monsters"""

        # print(cowsay.list_cows() + ['jgsbat'])
        try:
            x, y, hp, hello, name = self.addmon_params_check(args)
            self.s.sendall(f"addmon {name} {x} {y} {hp} {hello}\n".encode())
        except Exception:
            print(_('Smth wrong with this command'))

    def do_up(self, args):
        """Go up"""

        self.s.sendall(f"move 0 -1\n".encode())

    def do_down(self, args):
        """Go down"""

        self.s.sendall(f"move 0 1\n".encode())

    def do_left(self, args):
        """Go left"""

        self.s.sendall(f"move -1 0\n".encode())

    def do_right(self, args):
        """Go right"""

        self.s.sendall(f"move 1 0\n".encode())

    def do_movemonsters(self, args):
        """Movemonster commad realization"""

        # print(f'ARGS = {args}')
        if args in ['on', 'off']:
            self.s.sendall(f"movemonsters {args}\n".encode())
        else:
            print(_('Incorrect mode'))
            return

    def do_locale(self, loca):
        """Chose locale"""

        if loca in ['en_US.UTF8', 'ru_RU.UTF8']:
            self.s.sendall(f"locale {loca}\n".encode())
            if loca == 'en_US.UTF8':
                gamer_loca = ("en_US", "UTF-8")
            else:
                gamer_loca = ("ru_RU", "UTF-8")
            locale.setlocale(locale.LC_ALL, gamer_loca)
        else:
            print(_('Choose another locale'))
            return

    def do_attack(self, args):
        """Attack monster checker"""

        if len(args) == 0:
            print(
                _('Invalid input. You should provide at least name of the monster to attack'))
            return

        available_weapons = ['sword', 'spear', 'axe']
        weapon = 'sword'
        args = shlex.split(args)
        if 'with' in args:  # Мы передали на вход какое-то оружие
            weapon = args[-1]
        if weapon not in available_weapons:
            print(_('Unknown weapon'))
            return

        self.s.sendall(f"attack {weapon} {args[0]}\n".encode())

    def complete_attack(self, text, line, begidx, endidx):
        """Fase attack command helper"""
        words = (line[:endidx] + ".").split()
        DICT = []
        available_monsters = cowsay.list_cows() + ['jgsbat']

        match len(words):
            case 2:  # attack ...
                DICT = available_monsters
            case 3:  # attack <name> ...
                DICT = ['with']
            case 4:  # attack <name> with ...
                DICT = ['sword', 'spear', 'axe']

        words[-1] = words[-1].replace('.', '')
        return [c for c in DICT if c.startswith(text)]

    def complete_addmon(self, text, line, begidx, endidx):
        """Fast addmon command helper"""

        words = (line[:endidx] + ".").split()
        DICT = []
        available_monsters = cowsay.list_cows() + ['jgsbat']

        match len(words):
            case 2:  # attack ...
                DICT = available_monsters

        words[-1] = words[-1].replace('.', '')
        return [c for c in DICT if c.startswith(text)]

    def do_sayall(self, args):
        """Send msg to all users"""

        if len(args) == 0:
            print(_("You should input your message to others"))
            return

        self.s.sendall(f"sayall {' '.join(shlex.split(args))}\n".encode())

    def do_EOF(self, *args):
        """Exit game"""

        return 1

    def from_srv(self, cmdline, s):
        """Check msg from server"""

        while response := s.recv(1024).rstrip().decode():
            print(
                f"\n{response}\n{
                    cmdline.prompt}{
                    readline.get_line_buffer()}",
                end="",
                flush=True)
