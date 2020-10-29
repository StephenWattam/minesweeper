

import pygame

from board import BOMB

# Run until the user asks to quit
HIDDEN_COLOUR   = (128, 128, 128)
FLAG_COLOUR     = (0, 255, 0)
REVEALED_COLOUR = (50, 50, 50)
BOMB_COLOUR     = (255, 0, 0)

ADJACENCY_COLOURS = [(0, 0, 0), (0, 0, 128), (0, 128, 0), (0, 128, 128), (128, 0, 0),
                    (0, 0, 255), (0, 255, 0), (0, 255, 255), (255, 0, 0)]

# FIXME: may vary by platform
FONT = "dejavusans"

def render_interactive_board(board, game):

    pygame.init()

    # Set up the drawing window
    screen = pygame.display.set_mode([1500, 1500], pygame.RESIZABLE)

    running = True
    mouse_button_down = None
    while running:

        # Compute sizes of elements on the display for this refresh
        surface = pygame.display.get_surface() #get the surface of the current active display
        cell_width = surface.get_width() / board.width()
        cell_height = surface.get_height() / board.height()
        number_font = pygame.font.SysFont(FONT, int(min(cell_width, cell_height)))

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                left, mid, right = pygame.mouse.get_pressed()
                if left:
                    mouse_button_down = "left"
                elif right:
                    mouse_button_down = "right"

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                cell_x = int(pos[0] / cell_width)
                cell_y = int(pos[1] / cell_height)

                if mouse_button_down == "left":
                    game.click(cell_x, cell_y)
                elif mouse_button_down == "right":
                    game.toggle_flag(cell_x, cell_y)
                mouse_button_down = None

        # Fill the background with white
        screen.fill((255, 255, 255))

        # Check if we've won a print a message
        # TODO
        if game.finished:
            print(f"Game finished.")
            if game.won:
                print(f"You won!")
            else:
                print(f"You lost.")
            print(f"Moves: {game.moves}")
            running = False

        # Iterate over cells and render them
        for x, y, state in board.cell_tuples():
            cell_revealed = game.cell_revealed(x, y)

            # Cell shading
            colour = HIDDEN_COLOUR
            number = None

            if game.cell_flagged(x, y):
                colour = FLAG_COLOUR

            if cell_revealed:
                if state == BOMB:
                    colour = BOMB_COLOUR
                else:
                    colour = REVEALED_COLOUR

                # If the state is a certain annotation
                if state != BOMB and state > 0:
                    number = number_font.render(str(state), False, ADJACENCY_COLOURS[state])

            cell_rect = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            pygame.draw.rect(screen, colour, cell_rect)

            if number:
                # Render the number centred at the point given
                screen.blit(number, ((x+1) * cell_width - (cell_width / 2 + number.get_width() / 2),
                                     (y+1) * cell_height - (cell_width / 2 + number.get_height() / 2)) )

        # Flip the display
        pygame.display.flip()

    # Done! Time to quit.
    pygame.quit()