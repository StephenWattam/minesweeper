



from board import Board, BOMB
from game import MineSweeperGame
from render import render_interactive_board
from ai import MineSweeperAI


board = Board(1000, 1000, 0.1)
game  = MineSweeperGame(board)
ai    = MineSweeperAI(game, board)

# --------------

render_interactive_board(board, game, ai)


