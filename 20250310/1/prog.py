import cowsay
import sys
from io import StringIO
import shlex
import readline
import cmd



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

    def move(self, where):
        if where == 'up':
            self.y -= 1
            if self.y < 0:
                self.y = 9

        if where == 'down':
            self.y += 1
            if self.y > 9:
                self.y = 0
        
        if where == 'left':
            self.x -= 1
            if self.x < 0:
                self.x = 9
        
        if where == 'right':
            self.x += 1
            if self.x > 9:
                self.x = 0
        
        print(f'Moved to ({self.x}, {self.y})')

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

    def encounter(self, x, y):
        m = self.pole[y][x]
        m.say_hi()

    def create_params(self, args):
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
        
        return params


    def do_addmon(self, s):
        s = shlex.split(s)
        s.insert(0, 'addmon') # Переделывать весь разбор строки по параметрам не хочется
        if len(s) < 9 or len(s) > 10:
            print("Invalid arguments")
            return
        try:
            params = self.create_params(s)
            if params['name'] in cowsay.list_cows() or params['name'] == 'jgsbat':

                m = Monster(params['coords'][0], params['coords'][1], params['hp'], params['name'], params['hello'])
                print(f'Added monster {m.name} to ({m.x}, {m.y}) saying {m.phrase} with hp={m.hp}')
                if (m.x,m.y) in self.monsters_coords:
                    print("Replaced the old monster")
                self.monsters_coords.add((m.x, m.y))
                self.pole[m.y][m.x] = m 
            else:
                print("Cannot add unknown monster")
        except ValueError:
            print("Invalid arguments")

    def check_pos(self):
        if (self.g.x,self.g.y) in self.monsters_coords:
            self.encounter(self.g.x, self.g.y)

    def do_up(self, s):
        self.g.move('up')
        self.check_pos()
    
    def do_down(self, s):
        self.g.move('down')
        self.check_pos()

    def do_left(self, s):
        self.g.move('left')
        self.check_pos()

    def do_right(self, s):
        self.g.move('right')
        self.check_pos()

    def do_attack(self, args):
        x = self.g.x
        y = self.g.y
        if (x,y) not in self.monsters_coords:
            print('No monster here')
        else:
            m = self.pole[y][x]
            damage = 0
            if m.hp >= 10:
                damage = 10
            else:
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


    def do_EOF(self, args):
        return 1



def print_pole(pole):
    ans = ''
    for i in range(len(pole)):
        ans = ''
        if el != '*':
            ans += el.name[0]
        else:
            ans += el
        print(ans)

if __name__ == '__main__':
    print('<<< Welcome to Python-MUD 0.1 >>>')
    MUD().cmdloop()


