#
# Dee's Flappy Bird Game (My Cip2025 Project Version 1.0)
#
# My code implements my own version of a simple Flappy Bird game with "Data Analytics" using Pygame.
# As someone who loves playing games and currently pursuing a specialization in Data Science, I decided 
# to create my own version of the game that features a playable game loop with collision detection, 
# scoring, and different game states (menu, playing, game over, statistics). I documented my project
# in detail so I can add and improve it with more features in the future -- Daniella Kim :))
#
# Key Features:
# - Classic Flappy Bird gameplay: control a bird, navigate through pipes.
# - Score tracking for each game session.
# - Real-time logging of game data (score, duration) to a CSV file.
# - In-game statistics display (total games, highest score, average score).
# - Integration with an external Python script (`dee_dashboard.py`) to visualize
#   game statistics using Matplotlib, providing insights into player performance.
# - Dynamic background and ground scrolling for a visually engaging experience.
#
# Project Structure:
# - dee_main.py: The main game logic, event handling, and drawing.
# - dee_bird.py: Defines the Bird class (player character).
# - dee_pipe.py: Defines the Pipe class (obstacles).
# - dee_assets/ : Folder containing game images and fonts.
# - dee_data/ : Folder to store the game_log.csv data file.
# - dee_analysis/dee_dashboard.py: Script for generating graphical statistics.
#
# Libraries Used:
# - Pygame: For game development (graphics, input, sound, game loop).
# - os: For path manipulation and directory creation.
# - sys: For system-specific functions (e.g., exiting the program).
# - random: For randomizing pipe positions.
# - datetime: For timestamping game logs.
# - csv: For reading/writing game data to CSV.
# - pandas: For efficient data handling and statistical calculations from the CSV.
# - subprocess: To run the external dashboard script.
#
# How to Run:
# Make sure that all required Python packages (pygame, pandas) are installed.
# Run this script directly: `python dee_main.py`


import pygame      
import sys         
import os          
import random      
import datetime    
import csv         
import pandas as pd 
import subprocess

# Import custom game object classes
from dee_bird import Bird
from dee_pipe import Pipe


# --- 1. Game Constants ---
# Define screen dimensions for the game window
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

# Define commonly used RGB color tuples
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Game speed and frames per second (FPS)
FPS = 60

# Constants for game elements
GROUND_HEIGHT = 80       # Height of the ground area at the bottom of the screen
PIPE_GAP = 110           # Vertical gap size between top and bottom pipes
PIPE_SPAWN_INTERVAL = 1500 # Time in milliseconds between new pipe spawns
PIPE_SCROLL_SPEED = 2    # Speed at which pipes move left across the screen

# Paths for game assets (images, fonts) and data (game logs)
# os.path.dirname(__file__) gets the directory of the current script (dee_main.py)
# os.path.dirname(os.path.dirname(__file__)) goes up one level to the project root
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dee_assets")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dee_data")
os.makedirs(DATA_PATH, exist_ok=True)
GAME_LOG_FILE = os.path.join(DATA_PATH, "game_log.csv")

# Path to the external dashboard script, assuming it's in a 'dee_analysis' folder
DASHBOARD_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dee_analysis", "dee_dashboard.py")

# --- Font Path Constant ---
FONT_PATH = os.path.join(ASSETS_PATH, "PressStart2P-Regular.ttf")


# --- 2. Game States ---
# Define discrete states for the game flow
GAME_STATE_MENU = 0         # Main menu screen
GAME_STATE_PLAYING = 1      # Game is actively running
GAME_STATE_GAME_OVER = 2    # Game has ended, showing score and restart option
GAME_STATE_STATISTICS = 3   # Displaying game statistics (new screen)


# --- 3. Initialize Pygame ---
# Attempt to initialize all Pygame modules
try:
    pygame.init()
    print("Pygame initialized successfully!")
except Exception as e:
    print(f"Error initializing Pygame: {e}")
    sys.exit() # Exit if Pygame fails to initialize

# --- 4. Set up the display surface (the game window) ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Create the game window
pygame.display.set_caption("Dee's Flappy Bird") # Set the window title

# --- 5. Game Clock ---
clock = pygame.time.Clock() # Create a clock object to control frame rate

# --- 6. Custom Events (for pipe spawning) ---
SPAWNPIPE = pygame.USEREVENT # Define a custom event ID for pipe spawning

# --- 7. Fonts for Score & UI Display ---
pygame.font.init() # Initialize the font module
game_font = pygame.font.Font(FONT_PATH, 13)       # Font for in-game score and general text
title_font = pygame.font.Font(FONT_PATH, 15)      # Font for main titles (e.g., "GAME OVER")
instruction_font = pygame.font.Font(FONT_PATH, 8) # Smaller font for instructions
button_font = pygame.font.Font(FONT_PATH, 10)     # Font for button text


# --- 8. Load Game Assets ---
background_image = None 
ground_image = None

try:
    # Load background image and scale it to fit screen height proportionally
    # Using 'sky_background.jpg' as per your latest provided code.
    loaded_bg = pygame.image.load(os.path.join(ASSETS_PATH, 'sky_background.jpg')).convert()

    # Calculate new width to maintain aspect ratio, scaling to SCREEN_HEIGHT
    scaled_bg_height = SCREEN_HEIGHT
    scaled_bg_width = int(loaded_bg.get_width() * (scaled_bg_height / loaded_bg.get_height()))
    background_image = pygame.transform.scale(loaded_bg, (scaled_bg_width, scaled_bg_height))

    # Load ground image and scale it to match GROUND_HEIGHT proportionally
    loaded_ground = pygame.image.load(os.path.join(ASSETS_PATH, 'ground.jpg')).convert_alpha()

    # Calculate new width to maintain aspect ratio
    scaled_ground_height = GROUND_HEIGHT
    scaled_ground_width = int(loaded_ground.get_width() * (scaled_ground_height / loaded_ground.get_height()))
    ground_image = pygame.transform.scale(loaded_ground, (scaled_ground_width, scaled_ground_height))

except pygame.error as e:
    # Fallback if image loading fails (e.g., file not found)
    print(f"Error loading background or ground images: {e}")

    # Note: The original prompt had 'sky2_background.jpg' here, but the provided code had 'sky_background.jpg'
    print("Please check that 'sky_background.jpg' and 'ground.jpg' are in the 'dee_assets' folder.")
    print("Defaulting to solid colors for background and ground.")
    background_image = None
    ground_image = None


# --- 9. Game Variables (to track game state, score, and statistics) ---
score = 0                   # Current score in the ongoing game
current_game_state = GAME_STATE_MENU # Starting state of the game
game_start_time = 0         # Timestamp when the current game started (for duration)
last_score = 0              # Score from the most recently completed game

# Dictionary to hold summarized game statistics
game_stats = {
    'total_games': 0,
    'highest_score': 0,
    'average_score': 0.0
}

# --- Scrolling Visuals Variables ---
# background_x: X-offset for panning the wider background image.
# We display a SCREEN_WIDTH slice of the background starting at background_x.
background_x = 0
ground_x = 0 # X-offset for scrolling the ground image.
BACKGROUND_SCROLL_SPEED = 0.5 # Slower scroll for background to create parallax
GROUND_SCROLL_SPEED = PIPE_SCROLL_SPEED # Ground scrolls at the same speed as pipes


# --- 10. Game Objects (Initial setup) ---
bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, ASSETS_PATH) # Initialize the bird object
pipes = [] # List to hold active pipe objects


# --- 11. Drawing Functions ---
def display_score():
    """Draws the current score on the screen."""
    score_surface = game_font.render(str(int(score)), True, BLACK) # Render score text
    score_rect = score_surface.get_rect(center = (SCREEN_WIDTH // 2, 50)) # Center it at top
    screen.blit(score_surface, score_rect) # Draw to screen

def get_game_statistics():
    """
    Loads game data from the CSV log file and calculates statistics.
    Returns a dictionary with total games, highest score, and average score.
    """
    stats = {
        'total_games': 0,
        'highest_score': 0,
        'average_score': 0.0
    }
    if not os.path.exists(GAME_LOG_FILE):
        return stats # Return default stats if log file doesn't exist yet

    try:
        # Read CSV into a pandas DataFrame
        df = pd.read_csv(GAME_LOG_FILE, parse_dates=['timestamp'])

        # Convert score and duration to numeric, coercing errors to NaN
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
        df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce')

        # Drop rows with NaN values in score or duration (corrupted data)
        df.dropna(subset=['score', 'duration_seconds'], inplace=True)

        if not df.empty:
            # Calculate statistics if DataFrame is not empty
            stats['total_games'] = df.shape[0]          # Number of rows = total games
            stats['highest_score'] = int(df['score'].max()) # Maximum score
            stats['average_score'] = df['score'].mean()     # Mean score
        
    except pd.errors.EmptyDataError:
        print("Game log is empty, no stats to display yet.")
    except Exception as e:
        print(f"Error loading game statistics: {e}")
    return stats

def display_statistics_screen(stats_data):
    """
    Draws the game statistics screen including textual stats and navigation options.
    Returns the Rect object of the "VIEW GRAPHS" button for click detection.
    """
    stats_title_surface = title_font.render("GAME STATISTICS", True, BLACK)
    stats_title_rect = stats_title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(stats_title_surface, stats_title_rect)

    # Display total games played
    total_games_text = f"Games Played: {stats_data['total_games']}"
    total_games_surface = game_font.render(total_games_text, True, BLACK)
    total_games_rect = total_games_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(total_games_surface, total_games_rect)

    # Display highest score achieved
    highest_score_text = f"Highest Score: {stats_data['highest_score']}"
    highest_score_surface = game_font.render(highest_score_text, True, BLACK)
    highest_score_rect = highest_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(highest_score_surface, highest_score_rect)

    # Display average score
    average_score_text = f"Average Score: {stats_data['average_score']:.2f}"
    average_score_surface = game_font.render(average_score_text, True, BLACK)
    average_score_rect = average_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(average_score_surface, average_score_rect)

    # "Back to Menu" instruction (Changed color to BLACK for consistency)
    back_instruction_surface = instruction_font.render("Press ENTER to Back", True, BLACK)
    back_instruction_rect = back_instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    screen.blit(back_instruction_surface, back_instruction_rect)

    # "View Graphs" Button
    view_graphs_surface = button_font.render("VIEW GRAPHS", True, WHITE)
    view_graphs_rect = view_graphs_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140)) 
    pygame.draw.rect(screen, BLACK, view_graphs_rect.inflate(20, 10), border_radius=5) 
    screen.blit(view_graphs_surface, view_graphs_rect) 

    # "Press 'G' for Graphs" instruction
    g_key_instruction_surface = instruction_font.render("Press 'G' for Graphs", True, BLACK)
    g_key_instruction_rect = g_key_instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 110))
    screen.blit(g_key_instruction_surface, g_key_instruction_rect)

    return view_graphs_rect

def display_menu_screen():
    """Draws the main menu screen with title and play instruction."""
    title_surface = title_font.render("DEE'S", True, BLACK)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3.6))
    screen.blit(title_surface, title_rect)

    title_surface = title_font.render("FLAP & TRACK", True, BLACK)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(title_surface, title_rect)

    instruction_surface = instruction_font.render("Press SPACE to Play", True, BLACK)
    instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
    screen.blit(instruction_surface, instruction_rect)

def display_game_over_screen():
    """
    Draws the game over screen with final score, restart instruction,
    and a button/instruction to view statistics.
    Returns the Rect object of the "STATISTICS" button for click detection.
    """
    game_over_surface = title_font.render("GAME OVER", True, BLACK)
    # Adjusted position for game over text
    game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3.2))
    screen.blit(game_over_surface, game_over_rect)

    final_score_text = f"Score: {int(last_score)}"
    final_score_surface = game_font.render(final_score_text, True, BLACK)
    # Adjusted position for final score text
    final_score_rect = final_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.8))
    screen.blit(final_score_surface, final_score_rect)

    # Instruction for restarting the game
    restart_instruction_surface = instruction_font.render("Press SPACE to Restart", True, BLACK)
    restart_instruction_rect = restart_instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(restart_instruction_surface, restart_instruction_rect)
    
    # Statistics Button
    stats_button_surface = button_font.render("STATISTICS", True, WHITE)
    stats_button_rect = stats_button_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
    pygame.draw.rect(screen, BLACK, stats_button_rect.inflate(20, 10), border_radius=5) 
    screen.blit(stats_button_surface, stats_button_rect)

    # Instruction for 'S' key shortcut to view statistics
    s_key_instruction_surface = instruction_font.render("Press 'S' for Stats", True, BLACK)
    s_key_instruction_rect = s_key_instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 125))
    screen.blit(s_key_instruction_surface, s_key_instruction_rect)

    return stats_button_rect


# --- 12. Collision Check Function ---
def check_collision(bird_rect, pipes_list, ground_height, screen_height):
    """
    Checks for collisions between the bird and pipes or ground/ceiling.
    Returns True if a collision occurs, False otherwise.
    """
    for pipe in pipes_list:

        # Check collision with top pipe or bottom pipe
        if bird_rect.colliderect(pipe.top_rect) or bird_rect.colliderect(pipe.bottom_rect):
            return True

    # Check collision with the ground or ceiling
    if bird_rect.bottom >= screen_height - ground_height or bird_rect.top <= 0:
        return True

    return False


# --- 13. Data Logging Function ---
def log_game_data(final_score, duration):
    """
    Appends game results (score and duration) to a CSV log file.
    Creates the file with headers if it doesn't exist.
    """
    file_exists = os.path.isfile(GAME_LOG_FILE) # Check if the CSV file already exists
    
    with open(GAME_LOG_FILE, 'a', newline='') as csvfile: # Open in append mode
        fieldnames = ['timestamp', 'score', 'duration_seconds']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader() # Write headers if the file is new

        # Write the game data row
        writer.writerow({
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'score': final_score,
            'duration_seconds': round(duration, 2)
        })
    print(f"Game data logged: Score={final_score}, Duration={round(duration, 2)}s")


# --- 14. Game Loop ---
def game_loop():
    """Main loop of the game, handling events, updates, and drawing."""
    # Declare global variables to allow modification within this function
    global score
    global current_game_state
    global game_start_time
    global last_score
    global background_x
    global ground_x
    global game_stats

    # Placeholders for button Rects. These are updated when their respective screens are drawn.
    stats_button_rect_for_click = None 
    view_graphs_button_rect_for_click = None 

    running = True # Flag to keep the game loop running
    while running:

        # --- 14a. Event Handling ---
        # Process all events in the Pygame event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # End the loop if the window close button is pressed
            
            if event.type == pygame.KEYDOWN: # If a key is pressed down
                if event.key == pygame.K_SPACE: # If the SPACE bar is pressed
                    if current_game_state == GAME_STATE_MENU:
                        # Transition from Menu to Playing state
                        current_game_state = GAME_STATE_PLAYING
                        game_start_time = pygame.time.get_ticks() # Record game start time
                        pygame.time.set_timer(SPAWNPIPE, PIPE_SPAWN_INTERVAL) # Start pipe spawning timer
                        bird.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2) # Reset bird position
                        bird.velocity = 0 # Reset bird velocity
                        pipes.clear() # Clear existing pipes
                        score = 0 # Reset score
                        background_x = 0 # Reset background scroll
                        ground_x = 0 # Reset ground scroll

                    elif current_game_state == GAME_STATE_PLAYING:
                        bird.flap() # Make the bird flap

                    elif current_game_state == GAME_STATE_GAME_OVER:
                        # Data is now logged immediately upon collision, so we don't log again here.
                        # This block now only handles the game reset for restart.
                        
                        # Transition from Game Over to Playing state (restart)
                        current_game_state = GAME_STATE_PLAYING
                        game_start_time = pygame.time.get_ticks()
                        pygame.time.set_timer(SPAWNPIPE, PIPE_SPAWN_INTERVAL)
                        bird.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
                        bird.velocity = 0
                        pipes.clear()
                        score = 0
                        background_x = 0
                        ground_x = 0
                
                # Handle ENTER key for navigating back from statistics screen
                if event.key == pygame.K_RETURN:
                    if current_game_state == GAME_STATE_STATISTICS:
                        current_game_state = GAME_STATE_MENU # Go back to main menu

                # Handle 'S' key for viewing statistics from Game Over screen
                if event.key == pygame.K_s:
                    if current_game_state == GAME_STATE_GAME_OVER:
                        game_stats = get_game_statistics() # Load latest stats (which includes the just-finished game -- dee)
                        current_game_state = GAME_STATE_STATISTICS # Go to statistics screen

                # Handle 'G' key for viewing graphs from Statistics screen
                if event.key == pygame.K_g:
                    if current_game_state == GAME_STATE_STATISTICS:
                        print("Launching external dashboard via 'G' key...")
                        try:
                            # Use sys.executable to confirm the script is run with the correct Python interpreter
                            subprocess.Popen([sys.executable, DASHBOARD_SCRIPT_PATH])
                        except Exception as e:
                            print(f"Failed to launch dashboard: {e}")
                            print(f"Ensure '{DASHBOARD_SCRIPT_PATH}' exists and is a valid Python script.")


            if event.type == pygame.MOUSEBUTTONDOWN: # If a mouse button is clicked
                if event.button == 1: # Left mouse button
                    # Handle clicks on Game Over screen for the "STATISTICS" button
                    if current_game_state == GAME_STATE_GAME_OVER:
                        if stats_button_rect_for_click and stats_button_rect_for_click.collidepoint(event.pos):
                            game_stats = get_game_statistics() # Load latest stats (which includes the just-finished game -- dee)
                            current_game_state = GAME_STATE_STATISTICS # Go to statistics screen
                    
                    # Handle clicks on Statistics screen for the "VIEW GRAPHS" button
                    elif current_game_state == GAME_STATE_STATISTICS:
                        if view_graphs_button_rect_for_click and view_graphs_button_rect_for_click.collidepoint(event.pos):
                            print("Launching external dashboard via button click...")
                            try:
                                subprocess.Popen([sys.executable, DASHBOARD_SCRIPT_PATH]) # Launch the dashboard script
                            except Exception as e:
                                print(f"Failed to launch dashboard: {e}")
                                print(f"Ensure '{DASHBOARD_SCRIPT_PATH}' exists and is a valid Python script.")


            # Custom event for spawning pipes
            if event.type == SPAWNPIPE and current_game_state == GAME_STATE_PLAYING:
                pipes.append(Pipe(SCREEN_WIDTH, SCREEN_HEIGHT, PIPE_GAP, PIPE_SCROLL_SPEED, ASSETS_PATH))

        # --- 14b. Game Logic/Updates ---
        if current_game_state == GAME_STATE_PLAYING:
            bird.update() # Update bird's physics (gravity, flapping)

            # Update and manage pipes
            for pipe in pipes:
                pipe.update() # Move pipe to the left
                # Check if bird has passed the pipe (score increment)
                if pipe.top_rect.centerx < bird.rect.left and not pipe.passed:
                    score += 1
                    pipe.passed = True # Mark pipe as passed to prevent multiple scores
                
                # Remove pipes that have moved off-screen to save resources
                if pipe.top_rect.right < 0:
                    pipes.remove(pipe)

            # Update scrolling background (panoramic effect)
            background_x += BACKGROUND_SCROLL_SPEED
            if background_image:
                # If the current panoramic view goes beyond the image width, reset to start
                if background_x >= (background_image.get_width() - SCREEN_WIDTH):
                    background_x = 0

            # Update scrolling ground (tiling effect)
            ground_x -= GROUND_SCROLL_SPEED
            # If the ground image has scrolled entirely off-screen, reset its position
            if ground_x <= -ground_image.get_width():
                ground_x += ground_image.get_width()


            # Check for collisions after all updates
            if check_collision(bird.rect, pipes, GROUND_HEIGHT, SCREEN_HEIGHT):
                current_game_state = GAME_STATE_GAME_OVER # Transition to Game Over state
                last_score = score # Store the score of the just-finished game
                pygame.time.set_timer(SPAWNPIPE, 0) # Stop pipe spawning

                # --- NEW: Log game data immediately when game over occurs ---
                game_duration = (pygame.time.get_ticks() - game_start_time) / 1000
                log_game_data(last_score, game_duration)
                # --- END NEW ---

        # --- 14c. Drawing ---
        # Draw background image (or fallback color)
        if background_image:
            # Draw a slice of the wider background image to create the panning effect
            source_rect = pygame.Rect(background_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            screen.blit(background_image, (0,0), source_rect)
        else:
            screen.fill(SKY_BLUE) # Fallback to solid color if image failed to load

        # Draw pipes (only in playing or game over states)
        if current_game_state == GAME_STATE_PLAYING or current_game_state == GAME_STATE_GAME_OVER:
            for pipe in pipes:
                pipe.draw(screen)

        # Draw bird (always visible if game is active or over)
        bird.draw(screen)

        # Draw ground image (or fallback color)
        if ground_image:
            # Tile multiple copies of the ground image to create continuous scroll
            num_ground_tiles_to_draw = (SCREEN_WIDTH // ground_image.get_width()) + 2
            for i in range(num_ground_tiles_to_draw):
                screen.blit(ground_image, (ground_x + i * ground_image.get_width(), SCREEN_HEIGHT - ground_image.get_height()))
        else:
            # Fallback to solid brown rectangle if ground image failed to load
            ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
            pygame.draw.rect(screen, (139, 69, 19), ground_rect)

        # Draw UI elements based on current game state (drawn on top of game elements)
        if current_game_state == GAME_STATE_MENU:
            display_menu_screen()
            stats_button_rect_for_click = None # Reset button rects from other states
            view_graphs_button_rect_for_click = None
        elif current_game_state == GAME_STATE_PLAYING:
            display_score()
            stats_button_rect_for_click = None
            view_graphs_button_rect_for_click = None
        elif current_game_state == GAME_STATE_GAME_OVER:
            # Capture the button rect from display function for click detection
            stats_button_rect_for_click = display_game_over_screen()
            view_graphs_button_rect_for_click = None
        elif current_game_state == GAME_STATE_STATISTICS:
            # Capture the button rect from display function for click detection
            view_graphs_button_rect_for_click = display_statistics_screen(game_stats)
            stats_button_rect_for_click = None

        # Update the full display surface to show everything that's been drawn
        pygame.display.flip()
        # Cap the frame rate to FPS
        clock.tick(FPS)


    # --- 15. Quitting Pygame ---
    # Log final game data when the game loop ends, if a game was in progress or just ended
    # This specifically handles quitting the game from the PLAYING state (e.g., closing window),
    # ensuring data is still logged even if not reaching the GAME_OVER screen through collision.
    # The GAME_OVER state logging is handled within the main game logic now.
    if current_game_state == GAME_STATE_PLAYING and game_start_time != 0:
        game_duration = (pygame.time.get_ticks() - game_start_time) / 1000
        log_game_data(score, game_duration)

    # Uninitialize all pygame modules
    pygame.quit()
    # Exit the program
    sys.exit()

# --- 16. Run the game loop ---
# This confirms that game_loop() is called only when the script is executed directly
if __name__ == "__main__":
    game_loop()