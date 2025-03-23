import cowsay
import sys
from io import StringIO
import shlex
import readline
import cmd
import socket



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
    host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
    port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])

    def __init__(self, *args, socket, **kwargs):
        self.s = socket
        self.s.connect((self.host, self.port))
        return super().__init__(*args, **kwargs)
    
    def response_attack(self, name):
        response = self.s.recv(1024).rstrip().decode()
        if response == 'no':
            print(f"No {name} here")
            return
        damage, hp = [int(i) for i in response.split()]
        print(f"Attacked {name}, damage {damage} hp")
        if hp == 0:
            print(f"{name} died")
        else:
            print(f"{name} now has {hp}")
    
    def response_move(self):
        response = self.s.recv(1024).rstrip().decode().split()
        print(f"Moved to ({int(response[0])}, {int(response[1])})")
        if len(response) > 2:
            hello = ' '.join(response[3:])
            if response[2] == 'jgsbat':
                print(cowsay.cowsay(hello, cowfile=jgsbat))
            else:
                print(cowsay.cowsay(hello, cow=response[2]))



    def addmon_params_check(self, args):
        args = shlex.split(args)
        args.insert(0, 'addmon')
        params = {'name':'default', 'hello':'Uwu', 'hp':-1, 'coords':(0,0)}
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
            self.response_addmon(name, x, y, hello)
        except Exception as e:
            print('Smth wrong with this command')

    def response_addmon(self, name, x, y, hello):
        response = self.s.recv(1024).rstrip().decode()
        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
        if response == '1': print("Replaced the old monster")





    def do_attack(self, args):
        try:
            weapon, name = attack_check(args)
            self.s.sendall(f"attack {weapon} {name}\n".encode())
            self.response_attack(name)
        except Error as e:
            print(e.text)
    
    
    def do_up(self, args):
        if len(args) != 0:
            print(Error(1).text)
        else:
            self.s.sendall(f"move 0 -1\n".encode())
            self.response_move()

    def do_down(self, args):
        if len(args) != 0:
            print(Error(1).text)
        else:
            self.s.sendall(f"move 0 1\n".encode())
            self.response_move()

    def do_left(self, args):
        if len(args) != 0:
            print(Error(1).text)
        else:
            self.s.sendall(f"move -1 0\n".encode())
            self.response_move()

    def do_right(self, args):
        if len(args) != 0:
            print(Error(1).text)
        else:
            self.s.sendall(f"move 1 0\n".encode())
            self.response_move()
    

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
                DICT = [k for k,v in self.weapons.items()]

        words[-1] = words[-1].replace('.', '')
        return [c for c in DICT if c.startswith(text)]
    
    def do_EOF(self, *args):
        return 1

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client(socket=s).cmdloop()


