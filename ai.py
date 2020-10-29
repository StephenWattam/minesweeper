

FLAGGED = "f"

class MineSweeperAI:

    def __init__(self, game, board):

        self.game  = game
        self.board = board

    @staticmethod
    def _write_with_limit(obj, x, y, val):
        if x < 0 or x >= len(obj[0]):
            return
        if y < 0 or y >= len(obj):
            return

        obj[y][x] = val

    @staticmethod
    def _count_adjacent(obj, x, y, condition, skip_centre=True):
        count = 0
        which = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:

                # Skip centre
                if i == 0 and j == 0 and skip_centre:
                    continue

                if x+i < 0 or x+i >= len(obj[0]):
                    continue
                if y+j < 0 or y+j >= len(obj):
                    continue

                if condition(obj[y+j][x+i]):
                    count += 1
                    which.append( (x+i, y+j) )

        return count, which

    def move(self):

        # Things we know about the board, p[bomb]
        knowledge = [[None] * self.board.width() for _ in range(self.board.height())]

        # Precompute our view of the board, censored according to revealed status
        cells = [[self._observable_state(x, y) for x in range(self.board.width())] for y in range(self.board.height())]


        # PASS 1:
        # known facts about 0 cells
        for y in range(len(cells)):
            for x in range(len(cells[y])):
                # print(f"-> {x}, {y} = {cells[y][x]}")
                #self._prob(x, y, observations)

                state = cells[y][x]

                # Unknown cell --- not informative
                if state is None:
                    continue
                # Flagged cell --- not informative
                if state is FLAGGED:
                    knowledge[y][x] = 1
                    continue

                # Numbered cells definitely do not have bombs in
                knowledge[y][x] = 0

                # Anything around 0 doesn't have a bomb in
                if state == 0:
                    MineSweeperAI._write_with_limit(knowledge, x-1, y-1, 0)
                    MineSweeperAI._write_with_limit(knowledge, x,   y-1, 0)
                    MineSweeperAI._write_with_limit(knowledge, x+1, y-1, 0)
                    MineSweeperAI._write_with_limit(knowledge, x-1, y,   0)
                    MineSweeperAI._write_with_limit(knowledge, x+1, y,   0)
                    MineSweeperAI._write_with_limit(knowledge, x-1, y+1, 0)
                    MineSweeperAI._write_with_limit(knowledge, x,   y+1, 0)
                    MineSweeperAI._write_with_limit(knowledge, x+1, y+1, 0)

        # PASS 2
        # If a number has a certain number of unknowns, all are bombs
        for y in range(len(cells)):
            for x in range(len(cells[y])):

                state = cells[y][x]

                # Unknown cell: skip
                if state is None or state == FLAGGED:
                    continue

                if state > 0:
                    # Count adjacent unknowns
                    adjacent_unknown_count, coords = MineSweeperAI._count_adjacent(knowledge, x, y, lambda x: x is None or x == 1)

                    if adjacent_unknown_count == state:
                        for target_x, target_y in coords:
                            if not self.game.cell_flagged(target_x, target_y):
                                self.game.toggle_flag(target_x, target_y)
                                knowledge[target_y][target_x] = 1

        # PASS 3
        # After flagging, if something has only unknowns left, all are not bombs
        for y in range(len(cells)):
            for x in range(len(cells[y])):

                state = cells[y][x]

                # Unknown cell: skip
                if state is None or state == FLAGGED:
                    continue

                if state > 0:
                    # Count adjacent unknowns
                    adjacent_flag_count, _ = MineSweeperAI._count_adjacent(knowledge, x, y, lambda x: x == 1)
                    adjacent_unknown_count, coords = MineSweeperAI._count_adjacent(knowledge, x, y, lambda x: x is None)

                    if adjacent_flag_count == state and adjacent_unknown_count > 0:
                        for target_x, target_y in coords:
                            self.game.click(target_x, target_y)
                            knowledge[target_y][target_x] = 0


        # DEBUG
        # for row in knowledge:
        #     print(" ".join([str(x)[0] for x in row]))


    def _observable_state(self, x, y):
        """Return a flag used for the internal representation of what this AI can see right now,
        including the game hidden state.

        This ensures we don't accidentally cheat by looking at board info later"""

        if self.game.cell_flagged(x, y):
            return FLAGGED
        if not self.game.cell_revealed(x, y):
            return None

        # Read number from board
        return self.board.cell(x, y)
