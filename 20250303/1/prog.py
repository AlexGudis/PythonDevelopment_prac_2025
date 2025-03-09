import cowsay
import sys
from io import StringIO
import shlex



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

class MUD:
    def __init__(self):
        self.pole = [['*' for _ in range(10)] for _ in range(10)]
        self.monsters_coords = set()

    def encounter(self, x, y):
        m = self.pole[y][x]
        m.say_hi()

    def create_params(self, args):
        params = {'name':'default', 'hello':'Uwu', 'hp':-1, 'coords':(0,0)}

        params['name'] = args[args.index('addmon') + 1]
    
        try:
            params['hello'] = args[args.index('hello') + 1]
        except ValueError:
            raise ValueError
        
        try:
            params['hp'] = args[args.index('hp') + 1]
        except ValueError:
            raise ValueError
        
        try:
            start = args.index('coords')
            params['coords'] = (int(args[start + 1]), int(args[start + 2]))
        except ValueError:
            raise ValueError
        
        return params


    
    def play(self):
        g = Gamer(0, 0)
        while s := sys.stdin.readline():
            s = s[:-1]
            if s.startswith('addmon'):
                s = shlex.split(s)
                if len(s) < 9 or len(s) > 10:
                    print("Invalid arguments")
                    continue
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


            elif s == 'up' or s == 'down' or s == 'left' or s == 'right':
                g.move(s)
                if (g.x,g.y) in self.monsters_coords:
                    self.encounter(g.x, g.y)

            else:
                print('Invalid command')




def print_pole(pole):
    for el in pole:
        print(*el)


print('<<< Welcome to Python-MUD 0.1 >>>')
game = MUD()
game.play()

