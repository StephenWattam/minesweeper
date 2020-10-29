

FLAGGED = "f"

class MineSweeperAI:

    def __init__(game, board):

        self.game = game
        self.board = board

    def move(self):

        prob = [[None] * self.board.width() for _ in self.board.height()]

        # Precompute our view of the board, censored according to revealed status
        cell_locs = [(x, y) for x, y, state in self.board.cell_tuples()]
        cell_tuples = [(x, y, self._observable_state(x, y)) for x, y in cell_locs]

        # Keep track of minimums
        min_location = (0, 0)
        min_prob = 1
        for x in range(self.board.width()):
            for y in range(self.board.height()):
                # Compute p[bomb] for cell x, y
                pass

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

    def _prob(self, x, y):
        """Look at the information on the screen and identify p[bomb] for this cell"""

        pass
