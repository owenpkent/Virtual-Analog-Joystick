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
SLIDER_CIRCLE_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
CIRCLE_RADIUS = 20
SLIDER_WIDTH = 40
PADDING = 10

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
dragging_slider = False

# Variables for detecting double clicks
click_times = [0, 0]

# Initial position of the throttle slider
slider_position = HEIGHT - PADDING - CIRCLE_RADIUS

class Button:
    def __init__(self, x, y, width, height, color, text, text_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.text_color = text_color

    def draw(self, window, font):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        text_surface = font.render(self.text, True, self.text_color)
        window.blit(text_surface, (self.x + self.width // 2 - text_surface.get_width() // 2,
                                   self.y + self.height // 2 - text_surface.get_height() // 2))

    def is_over(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height

# Create a grid of buttons
BUTTON_WIDTH, BUTTON_HEIGHT = 30, 30
BUTTON_PADDING = 10
BUTTON_COLOR = (0, 128, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)
buttons = [[Button(WIDTH // 2 - 1.5 * BUTTON_WIDTH - 1.5 * BUTTON_PADDING + i * (BUTTON_WIDTH + BUTTON_PADDING),
                   HEIGHT - 4 * BUTTON_HEIGHT - 3 * BUTTON_PADDING + j * (BUTTON_HEIGHT + BUTTON_PADDING),
                   BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, f"{i+1 + j*4}", BUTTON_TEXT_COLOR)
            for i in range(4)] for j in range(3)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

            # Update the circle's position to stay within the new window size
            circle_position[0] = min(max(circle_position[0], CIRCLE_RADIUS), WIDTH - CIRCLE_RADIUS)
            circle_position[1] = min(max(circle_position[1], CIRCLE_RADIUS), HEIGHT - CIRCLE_RADIUS)

            # Update buttons' positions according to new window size
            for i, button_row in enumerate(buttons):
                for j, button in enumerate(button_row):
                    button.x = WIDTH // 2 - 1.5 * BUTTON_WIDTH - 1.5 * BUTTON_PADDING + j * (BUTTON_WIDTH + BUTTON_PADDING)
                    button.y = HEIGHT - 4 * BUTTON_HEIGHT - 3 * BUTTON_PADDING + i * (BUTTON_HEIGHT + BUTTON_PADDING)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_times = [click_times[-1], time.time()]

            if click_times[-1] - click_times[-2] < 0.3:  # detect double click
                circle_position[0] = WIDTH // 2

            if (event.pos[0] - circle_position[0])**2 + (event.pos[1] - circle_position[1])**2 < CIRCLE_RADIUS**2:
                dragging = True

            if WIDTH - PADDING - SLIDER_WIDTH // 2 - CIRCLE_RADIUS < event.pos[0] < WIDTH - PADDING + SLIDER_WIDTH // 2 + CIRCLE_RADIUS and \
               PADDING < event.pos[1] < HEIGHT - PADDING:
                dragging_slider = True

            for i, button_row in enumerate(buttons):
                for j, button in enumerate(button_row):
                    if button.is_over(event.pos):
                        print(f"Button {i+1 + j*4} pressed")
                        joystick.set_button(i+1 + j*4, 1)

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            dragging_slider = False
            for i in range(1, 13):
                joystick.set_button(i, 0)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # recenter on spacebar press
                circle_position = [WIDTH // 2, HEIGHT // 2]

    if dragging:
        mouse_pos = pygame.mouse.get_pos()
        circle_position = [min(max(mouse_pos[0], CIRCLE_RADIUS), WIDTH - CIRCLE_RADIUS),
                           min(max(mouse_pos[1], CIRCLE_RADIUS), HEIGHT - CIRCLE_RADIUS)]

    if dragging_slider:
        mouse_pos = pygame.mouse.get_pos()
        slider_position = min(max(mouse_pos[1], PADDING + CIRCLE_RADIUS), HEIGHT - PADDING - CIRCLE_RADIUS)

    window.fill(BACKGROUND_COLOR)

    pygame.draw.circle(window, CIRCLE_COLOR, circle_position, CIRCLE_RADIUS)

    pygame.draw.line(window, CIRCLE_COLOR, (WIDTH - PADDING - SLIDER_WIDTH // 2, PADDING), 
                     (WIDTH - PADDING - SLIDER_WIDTH // 2, HEIGHT - PADDING), SLIDER_WIDTH)

    pygame.draw.circle(window, SLIDER_CIRCLE_COLOR, (WIDTH - PADDING - SLIDER_WIDTH // 2, slider_position), CIRCLE_RADIUS)

    displacement = (int((circle_position[0] - WIDTH // 2) / (WIDTH // 2) * 16384), 
                    int(-(circle_position[1] - HEIGHT // 2) / (HEIGHT // 2) * 16384))

    text_surface = font.render(f"Displacement: ({displacement[0] // 164}, {displacement[1] // 164})", True, TEXT_COLOR)
    window.blit(text_surface, (10, 10))

    joystick.set_axis(pyvjoy.HID_USAGE_X, displacement[0] + 16384)
    joystick.set_axis(pyvjoy.HID_USAGE_Y, displacement[1] + 16384)

    throttle = 32768 - int((slider_position - PADDING - CIRCLE_RADIUS) / (HEIGHT - 2 * PADDING) * 32768)

    joystick.set_axis(pyvjoy.HID_USAGE_Z, throttle)

    throttle_percentage = 100 - int((slider_position - PADDING - CIRCLE_RADIUS) / (HEIGHT - 2 * PADDING) * 100)

    throttle_text_surface = font.render(f"Throttle: {throttle_percentage}%", True, TEXT_COLOR)
    window.blit(throttle_text_surface, (10, HEIGHT - PADDING - font.get_height()))

    for button_row in buttons:
        for button in button_row:
            button.draw(window, font)

    pygame.display.flip()
