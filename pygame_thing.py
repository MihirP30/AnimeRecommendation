import pygame
import sys
from proj2 import build_anime_graph  # replace with your filename if needed

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
FONT = pygame.font.SysFont("arial", 24)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Anime Recommendation System")

# Load anime graph
csv_file = "CleanedAnimeList.csv"
anime_graph, title_to_id, anime_data = build_anime_graph(csv_file)

# UI Elements
input_box = pygame.Rect(200, 200, 400, 40)
submit_button = pygame.Rect(275, 260, 250, 40)
user_text = ''
recommendation = ''
error_message = ''


def draw():
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, input_box, 2)
    pygame.draw.rect(screen, BLUE, submit_button)

    # Render input text
    input_surface = FONT.render(user_text, True, BLACK)
    screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))

    # Button text
    button_text = FONT.render("Get Recommendation", True, WHITE)
    screen.blit(button_text, (submit_button.x + 10, submit_button.y + 8))

    # Recommendation text
    if recommendation:
        rec_text = FONT.render(f"Recommended: {recommendation}", True, BLACK)
        screen.blit(rec_text, (200, 340))

    if error_message:
        error_text = FONT.render(error_message, True, (255, 0, 0))
        screen.blit(error_text, (200, 380))

    pygame.display.flip()


# Main loop
running = True
active = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state if clicked inside input box
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False

            # Check for submit button
            if submit_button.collidepoint(event.pos):
                normalized = user_text.strip().lower()
                if normalized in title_to_id:
                    closest_id = anime_graph.find_closest_anime(title_to_id[normalized])
                    if closest_id:
                        recommendation = anime_data[closest_id][0]
                        error_message = ''
                    else:
                        recommendation = ''
                        error_message = 'No recommendations found.'
                else:
                    recommendation = ''
                    error_message = 'Anime not found. Please check your input.'

        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            elif event.key == pygame.K_RETURN:
                # Optional: handle return key the same as submit
                pass
            else:
                user_text += event.unicode

    draw()

pygame.quit()
sys.exit()
