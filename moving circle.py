import pygame
import sys
import pyvjoy
import time

# Initialize Pygame
pygame.init()

# Initialize vJoy device
joystick = pyvjoy.VJoyDevice(1)

# Set up some constants
BACKGROUND_COLOR = (255, 255, 255)
CIRCLE_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)
CIRCLE_RADIUS = 20

# Set up the drawing window
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
window.fill(BACKGROUND_COLOR)

# Set up the font for the text
font = pygame.font.Font(None, 36)

# Initial position of the circle
circle_position = [WIDTH // 2, HEIGHT // 2]

# Flag for mouse button down
dragging = False

# Variables for detecting double clicks
click_times = [0, 0]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            # Update the window size
            WIDTH, HEIGHT = event.size
            window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

            # Update the circle's position to stay within the new window size
            circle_position[0] = min(max(circle_position[0], CIRCLE_RADIUS), WIDTH - CIRCLE_RADIUS)
            circle_position[1] = min(max(circle_position[1], CIRCLE_RADIUS), HEIGHT - CIRCLE_RADIUS)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Update the click times
            click_times = [click_times[-1], time.time()]

            # Check if the time between the last two clicks is less than 0.5 seconds
            if click_times[-1] - click_times[-2] < 0.5:
                circle_position[0] = WIDTH // 2  # Reset the x-coordinate of the circle position

            dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            new_position = list(event.pos)

            # Make sure the circle stays within the window
            if CIRCLE_RADIUS <= new_position[0] <= WIDTH - CIRCLE_RADIUS and CIRCLE_RADIUS <= new_position[1] <= HEIGHT - CIRCLE_RADIUS:
                circle_position = new_position

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                circle_position = [WIDTH // 2, HEIGHT // 2]

    # Redraw the background and the circle
    window.fill(BACKGROUND_COLOR)
    pygame.draw.circle(window, CIRCLE_COLOR, circle_position, CIRCLE_RADIUS)

    # Calculate the displacement from the center, scale it to range from -16384 to 16384, and convert to integers
    displacement = (int((circle_position[0] - WIDTH // 2) / (WIDTH // 2) * 16384), 
                    int(-(circle_position[1] - HEIGHT // 2) / (HEIGHT // 2) * 16384)) # negative sign for Y to make up positive

    # Render the text
    text_surface = font.render(f"Displacement: ({displacement[0] // 164}, {displacement[1] // 164})", True, TEXT_COLOR)

    # Blit the text onto the window
    window.blit(text_surface, (10, 10))

    # Send the displacement to the vJoy joystick
    # vJoy's set_axis method requires a value between 1 and 32768, so we need to adjust the displacement
    joystick.set_axis(pyvjoy.HID_USAGE_X, displacement[0] + 16384)
    joystick.set_axis(pyvjoy.HID_USAGE_Y, displacement[1] + 16384)

    pygame.display.flip()
