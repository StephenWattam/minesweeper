"""Represents a game played upon a minesweeper board.

Encodes movement rules, and win/lose conditions."""

from enum import Enum

from .board import BOMB
FLAGGED = "f"

class MineSweeperGame:
    """A game played upon a board."""

    def __init__(self, board):
        """Create a new game for the board given.

        Parameters:
            board: The Board object to play upon.
        """

        self.board = board
        self.state = [[None
                       for _ in range(board.width())]
                       for _ in range(board.height())]

        # Keep a list of bombs for fast lookup, and count revealed cells
        self.flags          = set()
        self.bomb_index     = {(x, y) for x, y, state in self.board.cell_tuples() if state == BOMB}
        self.revealed_count = 0
        self.moves          = 0

        self.finished = False
        self.won      = False

    def cell_flagged(self, x, y):
        """Has the cell at x, y been flagged?

        Returns:
            True if the cell at x, y has been flagged by the user already, else False
        """

        return (x, y) in self.flags

    def cell_revealed(self, x, y):
        """Has the cell at x, y been revealed?"""

        if x < 0 or x >= len(self.state[0]):
            return None
        if y < 0 or y >= len(self.state):
            return None

        return self.state[y][x]

    def toggle_flag(self, x, y):
        self.moves += 1

        if self.cell_flagged(x, y):
            self.flags.remove((x, y))
        else:
            self.flags.add((x, y))

        self._check_win()

    def click(self, x, y):
        """Reveal cell at x, y.

        Parameters:
            x: The row to reveal
            y: The column to reveal
        """

        # Don't permit people to take actions over and over on
        # the same cell
        if self.cell_revealed(x, y) or self.cell_flagged(x, y):
            return

        self.moves += 1

        # Lose if clicking on a bomb
        if self.board.is_bomb(x, y):
            self.state[y][x]     = True
            self.revealed_count += 1
            self.finished = True
            self.won      = False
            return

        # If the number is not 0, don't fill
        if self.board.cell(x, y) > 0:
            self.state[y][x] = True
            self.revealed_count += 1

        # If clicking a number of 0, spider out and clear other cells
        elif self.board.cell(x, y) == 0:
            self._fill_click(x, y)

        # We may have won!
        self._check_win()

    def _fill_click(self, init_x, init_y):
        """Fill an area around the clicked area, revealing all cells that have 0 adjacent bombs.

        Iterative to prevent recursion issues with large maps.

        Parameters:
            init_x: The initial x-location (row) to start filling from
            init_y: The initial y-location (column) to start filling from
        """

        # Start looking all around the cell
        cell_stack = set([(init_x, init_y)])

        while len(cell_stack) > 0:
            x, y = cell_stack.pop()

            # Skip when exceeding board bounds
            if x < 0 or y < 0 \
               or x >= self.board.width() or y >= self.board.height():
                continue
            # Skip over already revealed cells
            if self.state[y][x]:
                continue

            # Set cell to be clicked
            self.state[y][x]     = True
            self.revealed_count += 1

            # If the cell state is 0, add immediate surroundings to cell_stack
            if not self.board.is_bomb(x, y) and self.board.cell(x, y) == 0:
                cell_stack.add((x-1, y-1))
                cell_stack.add((x  , y-1))
                cell_stack.add((x+1, y-1))
                cell_stack.add((x-1, y  ))
                cell_stack.add((x+1, y  ))
                cell_stack.add((x-1, y+1))
                cell_stack.add((x  , y+1))
                cell_stack.add((x+1, y+1))

    def board_width(self):
        return self.board.width()

    def board_height(self):
        return self.board.height()

    def cell(self, x, y):
        """Return this game's view of cell x, y."""

        if self.cell_flagged(x, y):
            return FLAGGED
        if not self.cell_revealed(x, y):
            return None

        # Read number from board
        return self.board.cell(x, y)

    def revealed_cell_tuples(self):
        tuples = [[(x, y, self.cell(x, y)) for x in range(self.board.width())
                   if self.cell_revealed(x, y)]
                   for y in range(self.board.height())]
        tuples = [item for sublist in tuples for item in sublist]
        return tuples

    def _check_win(self):
        """Scan through the bomb index and ensure all are unrevealed, but
        all other cells revealed."""

        if self.flags != self.bomb_index:
            return False

        if self.revealed_count == self.board.num_cells() - len(self.bomb_index):
            self.finished = True
            self.won = True
