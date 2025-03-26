import pygame
import sys
from proj2 import build_anime_graph
# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
GREEN = (34, 139, 34)
FONT = pygame.font.SysFont("arial", 24)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Anime Recommendation System")

# Load anime graph
csv_file = "CleanedAnimeList.csv"
anime_graph, title_to_id, anime_data = build_anime_graph(csv_file)

# UI Elements
input_box = pygame.Rect(200, 200, 400, 40)
submit_button = pygame.Rect(275, 260, 250, 40)
new_rec_button = pygame.Rect(275, 320, 250, 40)
reset_button = pygame.Rect(275, 380, 250, 40)
user_text = ''
recommendation = ''
error_message = ''
current_recs = []


def draw():
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, input_box, 2)
    pygame.draw.rect(screen, BLUE, submit_button)
    pygame.draw.rect(screen, GREEN, new_rec_button)
    pygame.draw.rect(screen, RED, reset_button)

    # Render input text
    input_surface = FONT.render(user_text, True, BLACK)
    screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))

    # Button texts
    submit_text = FONT.render("Get Recommendation", True, WHITE)
    screen.blit(submit_text, (submit_button.x + 10, submit_button.y + 8))

    new_text = FONT.render("Another Recommendation", True, WHITE)
    screen.blit(new_text, (new_rec_button.x + 10, new_rec_button.y + 8))

    reset_text = FONT.render("Reset", True, WHITE)
    screen.blit(reset_text, (reset_button.x + 90, reset_button.y + 8))

    # Recommendation text
    if recommendation:
        rec_text = FONT.render(f"Recommended: {recommendation}", True, BLACK)
        screen.blit(rec_text, (200, 440))

    if error_message:
        error_text = FONT.render(error_message, True, (255, 0, 0))
        screen.blit(error_text, (200, 480))

    if searching:
        elap = pygame.time.get_ticks() - search_start_time
        progress = min(elap / SEARCH_DURATION, 1)
        bar_width = 400
        bar_height = 20
        bar_x = (WIDTH - bar_width) // 2
        bar_y = 520
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, BLUE, (bar_x, bar_y, bar_width * progress, bar_height))
        loading_text = FONT.render("Searching...", True, BLACK)
        screen.blit(loading_text, (bar_x, bar_y - 30))

    pygame.display.flip()


# Main loop
searching = False
search_start_time = 0
SEARCH_DURATION = 3000  # 5 seconds in milliseconds
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

            # Submit button clicked
            if submit_button.collidepoint(event.pos) and not searching:
                normalized = user_text.strip().lower()
                if normalized in title_to_id:
                    searching = True
                    search_start_time = pygame.time.get_ticks()
                    error_message = ''
                else:
                    recommendation = ''
                    error_message = 'Anime not found. Please check your input.'
                    current_recs = []

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

            # New recommendation button clicked
            if new_rec_button.collidepoint(event.pos):
                normalized = user_text.strip().lower()
                if normalized in title_to_id:
                    all_recs = anime_graph.get_top_n_recommendations(title_to_id[normalized], n=5)
                    # Exclude the currently shown one
                    new_recs = [anime for anime in all_recs if anime_data[anime][0] != recommendation]
                    if new_recs:
                        current_recs = new_recs
                        recommendation = anime_data[current_recs[0]][0]
                    else:
                        error_message = "No other recommendations available."
                else:
                    error_message = "Anime not found. Please try again."

            # Reset button clicked
            if reset_button.collidepoint(event.pos):
                user_text = ''
                recommendation = ''
                error_message = ''
                current_recs = []

        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                user_text += event.unicode
    if searching:
        elapsed = pygame.time.get_ticks() - search_start_time
        if elapsed >= SEARCH_DURATION:
            normalized = user_text.strip().lower()
            closest_ids = anime_graph.find_closest_anime(title_to_id[normalized])
            if closest_ids:
                current_recs = [closest_ids] if isinstance(closest_ids, str) else closest_ids
                recommendation = anime_data[current_recs[0]][0]
                error_message = ''
            else:
                recommendation = ''
                error_message = 'No recommendations found.'
                current_recs = []
            searching = False

    draw()

pygame.quit()
sys.exit()
