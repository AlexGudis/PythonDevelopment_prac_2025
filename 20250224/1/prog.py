import cowsay
import sys

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
    def __init__(self, x, y, phrase=''):
        self.x = x
        self.y = y
        self.phrase = phrase

    def say_hi(self):
        print(cowsay.cowsay(self.phrase))

class MUD:
    def __init__(self):
        self.pole = [['*' for _ in range(10)] for _ in range(10)]
        self.monsters_coords = set()

    def encounter(self, x, y):
        m = self.pole[y][x]
        m.say_hi()

    
    def play(self):
        g = Gamer(0, 0)
        while s := sys.stdin.readline():
            s = s[:-1]
            #print(f'Input was = {s}')
            #print('Where do u want to go? Chose one option: up, down, left, right')
            if s.startswith('addmon'):
                s = s.split()
                if len(s) < 4:
                    print("Invalid arguments")
                    continue
                try:
                    x = int(s[1])
                    y = int(s[2])
                    hello = s[3]

                    m = Monster(x,y,hello)
                    print(f'Added monster to ({x}, {y}) saying {hello}')
                    if (x,y) in self.monsters_coords:
                        print("Replaced the old monster")
                    self.monsters_coords.add((m.x, m.y))
                    self.pole[y][x] = m


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


game = MUD()
game.play()

