

from random import random

BOMB = "b"

class Board:

    def __init__(self, w, h, density=0.2):

        self.cells = [[BOMB if random() < density else None
                        for _ in range(w)]
                        for _ in range(h)]

        for x in range(self.width()):
            for y in range(self.height()):

                # Skip bombs
                if self.is_bomb(x, y):
                    continue

                adjacent = [self.is_bomb(x-1, y-1), self.is_bomb(x  , y-1), self.is_bomb(x+1, y-1),
                            self.is_bomb(x-1, y  ),                         self.is_bomb(x+1, y  ),
                            self.is_bomb(x-1, y+1), self.is_bomb(x  , y+1), self.is_bomb(x+1, y+1)]

                self.cells[y][x] = sum(adjacent)

    def is_bomb(self, x, y):

        return self.cell(x, y) == BOMB

    def cell(self, x, y):

        if x < 0 or x >= len(self.cells[0]):
            return None
        if y < 0 or y >= len(self.cells):
            return None

        return self.cells[y][x]

    def width(self):
        return len(self.cells[0])

    def height(self):
        return len(self.cells)

    def num_cells(self):
        return self.width() * self.height()

    def cell_tuples(self):
        tuples = [[(x, y, self.cell(x, y)) for x in range(self.width())]
                   for y in range(self.height())]
        tuples = [item for sublist in tuples for item in sublist]
        return tuples
