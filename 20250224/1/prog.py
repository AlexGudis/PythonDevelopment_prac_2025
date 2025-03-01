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


