"""Represents a static minesweeper board.

The squares, the mines, the relation of squares and mines --- everything."""

from random import random

# How we will recognise a bomb on the board.
# Used by other components.
BOMB = "b"

class Board:
    """A single minesweeper board"""

    def __init__(self, w, h, density=0.2):
        """Create a board with the dimensions and bomb density given.

        Parameters:
            w: The width, in cells
            h: The height, in cells
            density: The density of bombs on this board, 0-1.
        """

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
        """Is the cell at x, y a bomb?

        Equivalent to #cell(x, y) == BOMB

        Parameters:
            x: The row
            y: The column

        Returns: True if the cell at x,y contains a bomb, else False
        """

        return self.cell(x, y) == BOMB

    def cell(self, x, y):
        """Returns the contents of cell x, y

        Parameters:
            x: The row
            y: The column

        Returns: An integer 0-8 indicating the number of adjacent bombs, or BOMB if this cell
                 contains a bomb."""

        if x < 0 or x >= len(self.cells[0]):
            return None
        if y < 0 or y >= len(self.cells):
            return None

        return self.cells[y][x]

    def width(self):
        """Returns the width of the board in cells."""

        return len(self.cells[0])

    def height(self):
        """Returns the height of the board in cells."""

        return len(self.cells)

    def num_cells(self):
        """Returns the number of cells in the board"""

        return self.width() * self.height()

    def cell_tuples(self):
        """Returns a list of 3-tuples describing the board.

        Each tuple consists of (x, y, state) where state is the response from #cell(x, y)."""

        tuples = [[(x, y, self.cell(x, y)) for x in range(self.width())]
                   for y in range(self.height())]
        tuples = [item for sublist in tuples for item in sublist]
        return tuples
