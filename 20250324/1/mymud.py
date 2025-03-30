import cowsay
import sys
from io import StringIO
import shlex
import readline
import cmd
import socket
import threading



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



class client(cmd.Cmd):
    prompt = 'MUD> '
    intro = "<<< Welcome to Python-MUD 0.1 >>>"

    readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))

    def __init__(self, *args, socket, **kwargs):
        self.s = socket
        return super().__init__(*args, **kwargs)


    def addmon_params_check(self, args):
        args = shlex.split(args)
        args.insert(0, 'addmon')
        params = {'name':'default', 'hello':'Uwu', 'hp':1, 'coords':(0,0)}
        params['name'] = args[args.index('addmon') + 1]
    
        try:
            params['hello'] = args[args.index('hello') + 1]
        except ValueError:
            print('Something wrong with hello string when trying to parse it to a monster')
            raise ValueError
        
        try:
            params['hp'] = int(args[args.index('hp') + 1])
            if params['hp'] <= 0:
                raise ValueError
        except ValueError:
            print('hp argument should be a positive integer')
            raise ValueError
        
        try:
            start = args.index('coords')
            params['coords'] = (int(args[start + 1]), int(args[start + 2]))
        except ValueError:
            print('Something wrong with coords when trying to parse it to a monster')
            raise ValueError
        
        return params['coords'][0], params['coords'][1], params['hp'], params['hello'], params['name']
    
    def do_addmon(self, args):
        try:
            x, y, hp, hello, name = self.addmon_params_check(args)
            self.s.sendall(f"addmon {name} {x} {y} {hp} {hello}\n".encode())
        except Exception as e:
            print('Smth wrong with this command')


    def do_up(self, args):
        self.s.sendall(f"move 0 -1\n".encode())

    def do_down(self, args):
        self.s.sendall(f"move 0 1\n".encode())

    def do_left(self, args):
        self.s.sendall(f"move -1 0\n".encode())

    def do_right(self, args):
        self.s.sendall(f"move 1 0\n".encode())


    def do_attack(self, args):
        if len(args) == 0:
            print('Invalid input. You should provide at least name of the monster to attack')
            return

        available_weapons =  ['sword', 'spear', 'axe']
        weapon = 'sword'
        args = shlex.split(args)
        if 'with' in args: # Мы передали на вход какое-то оружие
            weapon = args[-1]
        if weapon not in available_weapons:
            print('Unknown weapon')
            return
        
        self.s.sendall(f"attack {weapon} {args[0]}\n".encode())
    
    def complete_attack(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        DICT = []
        available_monsters = cowsay.list_cows() + ['jgsbat']

        match len(words):
            case 2: # attack ...
                DICT = available_monsters
            case 3: # attack <name> ...
                DICT = ['with']
            case 4: # attack <name> with ...
                DICT = ['sword', 'spear', 'axe']

        words[-1] = words[-1].replace('.', '')
        return [c for c in DICT if c.startswith(text)]
    
    def do_EOF(self, *args):
        return 1

    def from_srv(self, cmdline, s):
        while response := s.recv(1024).rstrip().decode():
            print(f"\n{response}\n{cmdline.prompt}{readline.get_line_buffer()}", end="", flush=True)

if __name__ == '__main__':
    host = "localhost" if len(sys.argv) < 3 else sys.argv[2]
    port = 1337 if len(sys.argv) < 4 else int(sys.argv[3])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((host, port))
    s.sendall(f"{sys.argv[1]}\n".encode())
    if s.recv(1024).rstrip().decode() == '1':
        print(f"Your login: {sys.argv[1]}")
        cmdline = client(socket=s)
        mes = threading.Thread(target=cmdline.from_srv, args=(cmdline, s))
        mes.start()
        cmdline.cmdloop()
    else:
        print("ERROR: Choose another login")
    s.shutdown(socket.SHUT_RDWR)


