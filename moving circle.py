import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)
CIRCLE_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)
CIRCLE_RADIUS = 20

# Set up the drawing window
window = pygame.display.set_mode((WIDTH, HEIGHT))
window.fill(BACKGROUND_COLOR)

# Set up the font for the text
font = pygame.font.Font(None, 36)

# Initial position of the circle
circle_position = (WIDTH // 2, HEIGHT // 2)

# Flag for mouse button down
dragging = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            new_position = event.pos

            # Make sure the circle stays within the window
            if CIRCLE_RADIUS <= new_position[0] <= WIDTH - CIRCLE_RADIUS and CIRCLE_RADIUS <= new_position[1] <= HEIGHT - CIRCLE_RADIUS:
                circle_position = new_position

    # Redraw the background and the circle
    window.fill(BACKGROUND_COLOR)
    pygame.draw.circle(window, CIRCLE_COLOR, circle_position, CIRCLE_RADIUS)

    # Calculate the displacement from the center, scale it to range from -100 to 100, and convert to integers
    displacement = (int((circle_position[0] - WIDTH // 2) / (WIDTH // 2) * 100), 
                    int(-(circle_position[1] - HEIGHT // 2) / (HEIGHT // 2) * 100)) # negative sign for Y to make up positive

    # Render the text
    text_surface = font.render(f"Displacement: {displacement}", True, TEXT_COLOR)

    # Blit the text onto the window
    window.blit(text_surface, (10, 10))

    pygame.display.flip()
