"""Acts on a minesweeper game automatically when requested.

The structure does not actually separate the AI from the game/board through a standard Player
interface, meaning the AI can cheat if it wishes.  It doesn't, though.  Honest."""

FLAGGED = "f"

class MineSweeperAI:
    """An AI for minesweeper.  self-documenting code, innit."""

    def __init__(self, game, board_density_threshold=0.2):
        """Create a new MineSweeperAI to play the game given on the board given.

        Parameters:
            game: The game object to play
            board_density_threshold: The proportion (0-1) of the board seen before the AI will use
                                     observed bombs to estimate remaining bomb probabilities.
        """

        self.game  = game
        self.board = game.board

        # Behaviour params

        # After seeing this proportion of the board, a routine will be run to estimate the probability
        # of seeing a mine in an unknown square
        self.board_density_threshold = board_density_threshold

    @staticmethod
    def _write_with_limit(obj, x, y, val):
        """Given a 2D array, obj structured such that obj[y][x] accesses row x and column y,
        write val into the array iff x and y are within the bounds of the array.

        Parameters:
            obj: The 2D array to write into
            x: The row offset, 0-based
            y: The column offset, 0-based
            val: The value to insert into the array, if in bounds
        """

        if x < 0 or x >= len(obj[0]):
            return
        if y < 0 or y >= len(obj):
            return

        obj[y][x] = val

    @staticmethod
    def _count_adjacent(obj, x, y, condition, skip_centre=True):
        """Given a 2D array, obj, such that obj[y][x] addresses column y at row x, count all
        cells such that condition(value) is true for all cells in a ring around x, y.

        This returns not just the count of cells, but also the cell addresses themselves as
        tuples of (x, y).  If skip_centre is set to True, we'll miss x,y itself.

        Essentially, we run condition like this:
          condition(obj[y-1][x-1])
          condition(obj[y-1][x])
          condition(obj[y-1][x+1])
          ...
        and count one if condition(...) is truthy.

        Parameters:
            obj: The 2D array to write into
            x: The row offset, 0-based
            y: The column offset, 0-based
            condition: A procedure to call with the value of obj[][] surrounding x,y
            skip_centre: True to avoid counting x,y itself

        Returns:
            count: A number showing how many times condition was true.  <=8 if skip_centre, else <=9
            which: A list of (x,y) tuples showing condition(obj[y][x]) == True
        """

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

    def _read_observable_state(self):
        """Get observable state and basic knowledge of the board.

        The cell list is formatted as in the board class: each entry in the array shows the status
        of the cell as known on the board.  This may be a number 0-8 showing the number of adjacent
        bombs, or 'f' if the cell is flagged by the user.  Bombs should never be returned as
        observing a bomb means the game must be over.

        Knowledge acts as a "todo list", it's a mask showing what the AI knows, vs what it does not.
        Cells in the knowledge array may be None, indicating total unknown state or a number between
        0 and 1 reflecting the absolute probability that the cell contains a bomb.

        Returns:
            cells: A 2D array with the observable state of each cell (see above)
            knowledge: A 2D array with knowledge about each cell
        """

        # Precompute our view of the board, censored according to revealed status
        cells = [[self._observable_state(x, y) for x in range(self.board.width())] for y in range(self.board.height())]

        # Things we know about the board, p[bomb]
        knowledge = [[None] * self.board.width() for _ in range(self.board.height())]

        # known facts about 0 cells
        for y in range(len(cells)):
            for x in range(len(cells[y])):
                # print(f"-> {x}, {y} = {cells[y][x]}")
                #self._prob(x, y, observations)

                state = cells[y][x]

                # Unknown cell --- not informative
                if state is None:
                    continue
                # Flagged cell --- we know it's not a bome
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

        return cells, knowledge

    def _move_determinstic(self):
        """Deduce the moves that are guaranteed to be correct due to the hints given by
        cell numbers.

        Returns only when all actions that could be taken have been taken"""

        # Have we done anything to change the board this tick?
        action_this_loop = True
        # Have we done anything at all this method?
        action = False
        while action_this_loop:

            cells, knowledge = self._read_observable_state()
            action_this_loop = False

            # PASS 1
            # If a number has a certain number of unknowns, all are bombs and should be set as such
            for y in range(len(cells)):
                for x in range(len(cells[y])):

                    state = cells[y][x]

                    # Unknown cell: skip
                    if state is None or state == FLAGGED:
                        continue

                    if state > 0:
                        # Count adjacent unknowns
                        adjacent_unknown_count, coords = MineSweeperAI._count_adjacent(knowledge, x, y, lambda x: x is None or x == 1)

                        # If we have exactly the number of unknowns as cell number, set all to flags.
                        # Because setting a cell as flagged in the game only affects a single cell we can keep
                        # track of the knowledge changes by dead reckoning, no need to re-read the board
                        if adjacent_unknown_count == state:
                            for target_x, target_y in coords:
                                if not self.game.cell_flagged(target_x, target_y):
                                    self.game.toggle_flag(target_x, target_y)
                                    action_this_loop = True
                                    knowledge[target_y][target_x] = 1


            # PASS 2
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

                        # Click to reveal those cells that are around these numbers but known to not be
                        # bombs
                        #
                        # After clicking we have to re-read the board because the click could have
                        # revealed a large area of board
                        if adjacent_flag_count == state and adjacent_unknown_count > 0:
                            for target_x, target_y in coords:
                                self.game.click(target_x, target_y)
                                action_this_loop = True
                                knowledge[target_y][target_x] = 0

            # Keep track for return of method
            action = action_this_loop or action

        # Say if we did anything during this method
        return action


    def _move_heuristic(self):
        """Look at unknown cells and score them for how likely they are to be mines.

        Select the least likely move.

        Returns after a single action."""

        cells, knowledge = self._read_observable_state()

        # Compute basic probability there is a mine left in any cell.
        # Do this by looking at what we know about the board, and assuming roughly uniform distribution,
        # that is, we known p[mine] by observing existing flags.
        #
        # Only do this if we have seen a certain area of the board
        #
        # FIXME: This is imperfect because cells are not entirely independent.
        num_flags = 0
        num_unknown = 0
        baseline_probability = 0
        for y in range(len(cells)):
            for x in range(len(cells[y])):
                if cells[y][x] is None:
                    num_unknown += 1
                elif cells[y][x] is FLAGGED:
                    num_unknown += 1
        if num_unknown > 0 and self.board.width() * self.board.height() / (num_unknown + num_flags):
            baseline_probability = num_flags / num_unknown

        # PASS 1
        # If a number has a certain number of unknowns, all are bombs and should be set as such
        unknown_cell_penalty = {}
        for y in range(len(cells)):
            for x in range(len(cells[y])):

                state = cells[y][x]

                # Look at unknowns only
                if state is not None:
                    continue

                # Cell with adjacent unknown.  We want to discount the number of known mines
                # around this cell, then penalise the unknown cells by however many mines are
                # left indicated.  The sum of these overlaps will be proportional to the probability
                # that the unknown cell is mined
                adjacent_numbered_count, coords = MineSweeperAI._count_adjacent(cells, x, y, lambda x: x is not None and x != FLAGGED)
                # print(f"Found {adjacent_numbered_count} numbered cells near {x},{y}: {coords} => {[cells[y][x] for y, x in coords]}")

                # If we find no numbered cells nearby, we simply have to guess at the basic probability
                # that there is a mine in this cell, independent of other cells.
                if adjacent_numbered_count == 0:
                    unknown_cell_penalty[(x, y)] = baseline_probability
                else:
                    # For each numbered cell, count the number of flags around it, and subtract
                    # that from its total
                    normalise = 0
                    for target_x, target_y in coords:
                        cell_number = cells[target_y][target_x]
                        # print(f" ## {cell_number} ({target_y}, {target_x})")
                        adjacent_flag_count, _ = MineSweeperAI._count_adjacent(cells, target_x, target_y, lambda x: x == FLAGGED)
                        remaining_adjacent_mines = cell_number - adjacent_flag_count

                        # print(f"# [{x}, {y}] -> {target_x}, {target_y} ({cell_number} - {adjacent_flag_count})")
                        # If this number still has some knowledge remaining, allocate evenly between cells we don't know about
                        # yet.
                        if remaining_adjacent_mines == 0:
                            continue

                        # We must be one of these remaining adjacent unknowns
                        remaining_unknown_count, _ = MineSweeperAI._count_adjacent(knowledge, target_x, target_y, lambda x: x == None)
                        penalty = remaining_adjacent_mines / remaining_unknown_count

                        # print(f"{remaining_adjacent_mines=}, {penalty=}")
                        if (x, y) not in unknown_cell_penalty:
                            unknown_cell_penalty[(x, y)] = 0 # FIXME: should this been baseline_probability?
                        unknown_cell_penalty[(x, y)] += penalty
                        normalise += 1

                    # Divide penalty by the number of cells that contributed it, i.e. normalise
                    unknown_cell_penalty[(x, y)] /= normalise


        if len(unknown_cell_penalty) == 0:
            # Can't do anything!
            return False

        # print(f" -> {unknown_cell_penalty}")
        # Find the lowest score and click it
        cell_coord, penalty = sorted(unknown_cell_penalty.items(), key=lambda item: item[1])[0]
        # print(f"Lowest penalty is #{cell_coord} with penalty={penalty}")
        self.game.click(cell_coord[0], cell_coord[1])
        return True


    def move(self):
        """Interface to AI classes, acting as a request to act on the game.

        Because the deterministic solver calls the game class directly, this may actually move
        more than once."""

        # Attempt deterministic actions
        action = self._move_determinstic()

        if not action:
            #print("No action from deterministic solver, using heuristics.")
            action = self._move_heuristic() or action
        else:
            pass
            #print("Determinstic solution used.")

        # DEBUG
        # for row in knowledge:
        #     print(" ".join([str(x)[0] for x in row]))


    def _observable_state(self, x, y):
        """Return a flag used for the internal representation of what this AI can see right now,
        including the game hidden state.

        This ensures we don't accidentally cheat by looking at board info later.

        Parameters:
            x: The x coordinate to extract from the board
            x: The y coordinate to extract from the board

        Returns:
            The value at x, y, subject to rules allowable for the game given
        """

        if self.game.cell_flagged(x, y):
            return FLAGGED
        if not self.game.cell_revealed(x, y):
            return None

        # Read number from board
        return self.board.cell(x, y)
