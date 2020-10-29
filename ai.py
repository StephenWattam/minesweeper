

FLAGGED = "f"

class MineSweeperAI:

    def __init__(self, game, board):

        self.game = game
        self.board = board

    def move(self):

        prob = [[None] * self.board.width() for _ in range(self.board.height())]

        # Precompute our view of the board, censored according to revealed status
        cells = [[self._observable_state(x, y) for x in range(self.board.width())] for y in range(self.board.height())]

        # Keep track of minimums
        min_location = (0, 0)
        min_prob = 1
        for y in range(len(cells)):
            for x in range(len(cells[y])):
                print(f"-> {x}, {y} = {cells[y][x]}")
                #self._prob(x, y, observations)

    def _observable_state(self, x, y):
        """Return a flag used for the internal representation of what this AI can see right now,
        including the game hidden state.

        This ensures we don't accidentally cheat by looking at board info later"""

        if not self.game.cell_revealed(x, y):
            return None
        if self.game.cell_flagged(x, y):
            return FLAGGED

        # Read number from board
        return self.board.cell(x, y)

    def _prob(self, x, y, observations):
        """Look at the information on the screen and identify p[bomb] for this cell"""




        pass
