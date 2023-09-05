import pygame
import time
import random

# Initialize Pygame
pygame.init()

# Constants for screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create a screen (window)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the title of the window
pygame.display.set_caption('Typing Speed Game')

# Function to display text
def display_text(text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to reset the game
def reset_game():
    global start_time, user_text, score, target_sentence
    start_time = None
    user_text = ""
    score = 0
    target_sentence = random.choice(sentences)

# List of potential target sentences
sentences = [
    "The quick brown fox jumps over the lazy dog",
    "A journey of a thousand miles begins with a single step",
    "To be or not to be, that is the question",
    "All that glitters is not gold",
    "Practice makes perfect"
]

# Pick a random target sentence
target_sentence = random.choice(sentences)

# Variable to hold the text entered by the user
user_text = ""

# Timer settings
start_time = None
time_limit = 60  # 60 seconds

# Score
score = 0
total_characters = 0
correct_characters = 0

# Game loop
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                game_over = False
                reset_game()
            elif not game_over:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                    # Ensure correct_characters does not go below zero
                    correct_characters = max(0, correct_characters - 1)
                elif event.key == pygame.K_RETURN:
                    if user_text == target_sentence:
                        print("Correct!")
                        score += 1
                        target_sentence = random.choice(sentences)
                        user_text = ""
                        correct_characters = 0
                    else:
                        print("Incorrect, try again.")
                else:
                    user_text += event.unicode
                    # Check if the added character is correct
                    if len(user_text) > 0 and len(user_text) <= len(target_sentence):
                        if user_text[-1] == target_sentence[len(user_text) - 1]:
                            correct_characters += 1
                
                    # Calculate and display typing accuracy
                    if len(target_sentence) > 0 and not game_over:  # To avoid division by zero
                        accuracy = (correct_characters / len(target_sentence)) * 100
                        display_text(f"Accuracy: {accuracy:.2f}%", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.7)


    if game_over:
        # Display Game Over screen
        screen.fill((0, 0, 0))
        display_text("Game Over", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        display_text(f"Your Score: {score}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        display_text("Press 'R' to restart", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
        pygame.display.update()
    else:
        # Handle the active game state
        current_time = time.time()
        if start_time is None:
            start_time = current_time
        elapsed_time = int(current_time - start_time)

        # Display game elements
        screen.fill((0, 0, 0))
        display_text(target_sentence, 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        display_text(user_text, 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        display_text(f"Time remaining: {time_limit - elapsed_time}s", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.2)
        display_text(f"Score: {score}", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)

        if time_limit - elapsed_time <= 0:
            print(f"Time's up! Your score is {score}")
            game_over = True

        pygame.display.update()

# Quit Pygame
pygame.quit()
