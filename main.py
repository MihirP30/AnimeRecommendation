"""
Anime Recommendation System

This file creates a graphical user interface (GUI) for an anime recommendation system. This program uses the Pygame
class to create the GUI for user inteaction and visualization, which it uses a recommendation software to create and
provide anime title recommendations.

The interface is implemented using Pygame,which provides functionalities like inputting text, creating buttons, progress
bars, etc. After launching the class and inputting an anime, users can reset the input or get another recommendation.

Modules:
    - pygame: Used to create the graphical user interface.
    - sys: Provides system-specific parameters and functions.
    - proj2: Program used to construct the graph and provide recommendations
"""

import pygame
import sys
from proj2 import build_anime_graph

# Initialize Pygame
pygame.init()

# Window size and colors
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
GREEN = (34, 139, 34)

# Font setup
FONT = pygame.font.SysFont("arial", 24)

#  Create Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Anime Recommendation System")

#  Load anime graph and data
csv_file = "SmallAnimeList.csv"
anime_graph, title_to_id, anime_data = build_anime_graph(csv_file)

# UI Element Rectangles
input_box = pygame.Rect(200, 200, 400, 40)
submit_button = pygame.Rect(275, 260, 250, 40)
new_rec_button = pygame.Rect(275, 320, 250, 40)
reset_button = pygame.Rect(275, 380, 250, 40)

#  State Variables
user_text = ''
recommendation = ''
pending_recommendation = ''
error_message = ''
pending_error = ''
current_recs = []
top_n_recs = []
closest_recommendation = ''
last_input = ''
rec_index = 0

# Progress bar control
searching = False
search_start_time = 0
SEARCH_DURATION = 4000  # 4 seconds
search_action = None  # "submit" or "new"
first_rec_done = False


def draw():
    """This function draws the user interface onto the screen, rendering the input box, buttons, recommendation, error
    messages, and progress bar. The interface is updated after all elements are drawn onto the screen.
    """
    screen.fill(WHITE)

    # Draw input box and buttons
    pygame.draw.rect(screen, GRAY, input_box, 2)
    button_color = BLUE if first_rec_done else GREEN
    pygame.draw.rect(screen, button_color, new_rec_button)
    pygame.draw.rect(screen, RED, reset_button)

    # Render user input
    input_surface = FONT.render(user_text, True, BLACK)
    screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))

    # Render button labels
    button_desc = "Recommend Another" if first_rec_done else "Get Recommendation"
    screen.blit(FONT.render(button_desc, True, WHITE), (new_rec_button.x + 10, new_rec_button.y + 8))
    screen.blit(FONT.render("Reset", True, WHITE), (reset_button.x + 90, reset_button.y + 8))

    # Display current recommendation
    if recommendation:
        rec_text = FONT.render(f"Recommended: {recommendation}", True, BLACK)
        screen.blit(rec_text, (200, 440))

    # Display error message if any
    if error_message:
        error_text = FONT.render(error_message, True, (255, 0, 0))
        screen.blit(error_text, (200, 480))

    # Progress bar animation
    if searching:
        elap = pygame.time.get_ticks() - search_start_time
        progress = min(elap / SEARCH_DURATION, 1)
        bar_width, bar_height = 400, 20
        bar_x = (WIDTH - bar_width) // 2
        bar_y = 520
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))  # background
        pygame.draw.rect(screen, BLUE, (bar_x, bar_y, bar_width * progress, bar_height))  # fill
        loading_text = FONT.render("Searching...", True, BLACK)
        screen.blit(loading_text, (bar_x, bar_y - 30))

    pygame.display.flip()


# Main Loop
running = True
active = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False

            # Recommendation Button Clicked
            if new_rec_button.collidepoint(event.pos) and not searching:
                search_action = 'new' if first_rec_done else 'submit'
                search_start_time = pygame.time.get_ticks()
                searching = True

            # Reset Button Clicked
            if reset_button.collidepoint(event.pos):
                user_text = ''
                recommendation = ''
                pending_recommendation = ''
                error_message = ''
                pending_error = ''
                current_recs = []
                top_n_recs = []
                closest_recommendation = ''
                last_input = ''
                rec_index = 0
                search_action = None
                searching = False
                first_rec_done = False

        # Handle keyboard input
        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            elif event.key == pygame.K_RETURN:
                pass  # Optional: trigger submit
            else:
                user_text += event.unicode

    # Handle delayed search logic after animation
    if searching:
        elapsed = pygame.time.get_ticks() - search_start_time
        if elapsed >= SEARCH_DURATION:
            normalized = user_text.strip().lower()

            if normalized in title_to_id and normalized != "":
                anime_id = title_to_id[normalized]

                if search_action == 'submit':
                    # Get closest recommendation
                    first_rec_done = True
                    closest_id = anime_graph.find_closest_anime(anime_id)
                    if closest_id:
                        closest_recommendation = anime_data[closest_id][0]
                        current_recs = [closest_id]
                        last_input = normalized
                        rec_index = 0
                        pending_recommendation = closest_recommendation
                        pending_error = ''
                        # Get top N excluding closest
                        all_recs = anime_graph.get_top_n_recommendations(anime_id, n=6)
                        top_n_recs = [rec for rec in all_recs if rec != closest_id]
                    else:
                        closest_recommendation = ''
                        current_recs = []
                        top_n_recs = []
                        pending_recommendation = ''
                        pending_error = 'No recommendations found.'

                if search_action == 'new':
                    if normalized != last_input:
                        closest_id = anime_graph.find_closest_anime(anime_id)
                        closest_recommendation = anime_data[closest_id][0] if closest_id else ''
                        last_input = normalized
                        all_recs = anime_graph.get_top_n_recommendations(anime_id, n=6)
                        top_n_recs = [rec for rec in all_recs if rec != closest_id]
                        rec_index = 0

                    if top_n_recs:
                        rec_index = (rec_index + 1) % len(top_n_recs)
                        rec_id = top_n_recs[rec_index]
                        pending_recommendation = anime_data[rec_id][0]
                        pending_error = ''
                    else:
                        pending_recommendation = ''
                        pending_error = "No other recommendations available."

            else:
                pending_recommendation = ''
                pending_error = "Anime not found. Please check your input."

            # Finalize after search delay
            recommendation = pending_recommendation
            error_message = pending_error
            pending_recommendation = ''
            pending_error = ''
            searching = False
            search_action = None

    draw()

# Exit
pygame.quit()
sys.exit()
