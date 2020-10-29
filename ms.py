



from board import Board, BOMB
from game import MineSweeperGame
from render import render_interactive_board


board = Board(100, 100, 0.05)
game = MineSweeperGame(board)


# --------------

render_interactive_board(board, game)


