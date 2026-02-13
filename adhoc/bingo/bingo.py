import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
FPS = 60

# Setup display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Bingo Number Generator")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 200)
small_font = pygame.font.Font(None, 32)

# Game state
current_number = None
drawn_numbers = []

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Get all numbers that haven't been drawn yet
                available_numbers = [n for n in range(1, 91) if n not in drawn_numbers]
                if available_numbers:
                    current_number = random.choice(available_numbers)
                    drawn_numbers.append(current_number)

    # Clear screen
    screen.fill(BACKGROUND_COLOR)

    # Draw number if one has been generated
    if current_number is not None:
        text_surface = font.render(str(current_number), True, TEXT_COLOR)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        screen.blit(text_surface, text_rect)
    else:
        # Draw instruction text
        instruction_font = pygame.font.Font(None, 48)
        instruction_surface = instruction_font.render(
            "Press SPACE to draw a number", True, TEXT_COLOR
        )
        instruction_rect = instruction_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        screen.blit(instruction_surface, instruction_rect)

    # Draw sorted list of drawn numbers at the bottom
    if drawn_numbers:
        sorted_numbers = sorted(drawn_numbers)
        numbers_text = ", ".join(str(n) for n in sorted_numbers)

        # Split into multiple lines if needed
        max_width = WINDOW_WIDTH - 40
        words = numbers_text.split(", ")
        lines = []
        current_line = []

        for word in words:
            test_line = ", ".join(current_line + [word]) if current_line else word
            test_surface = small_font.render(test_line, True, TEXT_COLOR)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(", ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(", ".join(current_line))

        # Draw the lines
        y_offset = WINDOW_HEIGHT - 20 - (len(lines) * 35)
        for i, line in enumerate(lines):
            line_surface = small_font.render(line, True, TEXT_COLOR)
            line_rect = line_surface.get_rect(
                center=(WINDOW_WIDTH // 2, y_offset + i * 35)
            )
            screen.blit(line_surface, line_rect)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
