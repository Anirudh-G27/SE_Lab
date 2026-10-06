import pygame
from game.game_engine import GameEngine


# ============================================================
# INITIALIZE PYGAME
# ============================================================

# Configure audio (mono, 16-bit, small buffer for low latency) BEFORE
# pygame.init(). If no audio device exists the game still runs silently.
try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
except pygame.error:
    pass

pygame.init()

# Screen dimensions
WIDTH = 600
HEIGHT = 500

# Create game window
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Marble Tilt Maze - Pygame Version")

# Game clock
CLOCK = pygame.time.Clock()

# Target FPS
FPS = 60


# ============================================================
# MAIN GAME
# ============================================================

def main():

    # Create the game engine
    engine = GameEngine(WIDTH, HEIGHT)

    running = True

    while running:

        # ----------------------------------------------------
        # HANDLE EVENTS
        # ----------------------------------------------------

        for event in pygame.event.get():

            # Window close button
            if event.type == pygame.QUIT:
                running = False
                continue

            # Pass event to the game engine
            result = engine.handle_event(event)

            # GameEngine can request application exit
            if result == "QUIT":
                running = False


        # ----------------------------------------------------
        # HANDLE KEYBOARD / MOUSE INPUT
        # ----------------------------------------------------

        if running:
            engine.handle_input()


        # ----------------------------------------------------
        # UPDATE GAME
        # ----------------------------------------------------

        if running:
            result = engine.update()

            # GameEngine can request application exit
            if result == "QUIT":
                running = False


        # ----------------------------------------------------
        # RENDER GAME
        # ----------------------------------------------------

        if running:
            engine.render(SCREEN)

            # Update display
            pygame.display.flip()


        # ----------------------------------------------------
        # LIMIT FPS
        # ----------------------------------------------------

        CLOCK.tick(FPS)


    # ========================================================
    # CLEANUP
    # ========================================================

    pygame.quit()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()