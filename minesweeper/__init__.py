"""Main entry point for minesweeper game."""

import os, sys

from .board import Board, BOMB
from .game import MineSweeperGame
from .render import render_interactive_board
from .ai import MineSweeperAI


# ----------------------------------------------------------------------------------
# Interactive mode!
def interactive():
    board = Board(20, 20, 0.05)
    game  = MineSweeperGame(board)
    ai    = MineSweeperAI(game)

    render_interactive_board(game, ai)


# ----------------------------------------------------------------------------------
# Batch mode to gather stats.
def batch():

    NUM_GAMES     = 100
    BOARD_WIDTH   = 100
    BOARD_HEIGHT  = 100
    BOARD_DENSITY = 0.2

    # 100 games
    log_wins = []
    log_moves = []
    for i in range(NUM_GAMES):

        board = Board(BOARD_WIDTH, BOARD_HEIGHT, BOARD_DENSITY)
        game  = MineSweeperGame(board)
        ai    = MineSweeperAI(game)

        while not game.finished:
            ai.move()

        log_wins.append(game.won)
        log_moves.append(game.moves)
        print(f"[{i}/{NUM_GAMES}] win? {game.won}, moves: {game.moves}")

    # Print summary
    print(f"Board with {BOARD_WIDTH}x{BOARD_HEIGHT} WxH, mine density={BOARD_DENSITY}")
    print(f"{sum(log_wins)} wins out of {len(log_wins)} games ({sum(log_wins) / len(log_wins) * 100:0.2f}%%)")
    print(f"{sum(log_moves) / len(log_moves):.2f} moves on average")
    without_lofc = [x for x in log_moves if x > 1]
    if len(without_lofc) > 0:
        print(f"{sum(without_lofc) / len(without_lofc):.2f} discounting lose-on-first-click")