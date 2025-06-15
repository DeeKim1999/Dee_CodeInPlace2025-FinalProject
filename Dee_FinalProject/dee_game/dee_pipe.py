import pygame
import random

# --- Constants for Pipe Colors ---
LIGHT_PURPLE = (200, 162, 222) 
DARK_PURPLE = (80, 50, 100)   
OUTLINE_THICKNESS = 2        

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, screen_height, pipe_gap, scroll_speed, assets_path):
        super().__init__()

        self.screen_height = screen_height
        self.pipe_gap = pipe_gap
        self.scroll_speed = scroll_speed

        pipe_width = 52 # Standard Flappy Bird pipe width

        # Generate a random height for the top pipe while ensuring enough space for gap and buffer
        min_top_pipe_height = 100
        max_top_pipe_height = self.screen_height - self.pipe_gap - min_top_pipe_height
        
        if max_top_pipe_height < min_top_pipe_height:
            max_top_pipe_height = min_top_pipe_height + 50

        top_pipe_height = random.randint(min_top_pipe_height, max_top_pipe_height)

        # Create surfaces for the top and bottom pipe rectangles (no image loading)
        self.top_pipe_image = pygame.Surface((pipe_width, top_pipe_height))
        self.bottom_pipe_image = pygame.Surface((pipe_width, self.screen_height - top_pipe_height - self.pipe_gap))

        # Fill the surfaces with our light purple color
        self.top_pipe_image.fill(LIGHT_PURPLE)
        self.bottom_pipe_image.fill(LIGHT_PURPLE)

        # Create rects for positioning (these define where the pipes are drawn and for collision)
        self.top_rect = self.top_pipe_image.get_rect(bottomleft=(x, top_pipe_height))
        self.bottom_rect = self.bottom_pipe_image.get_rect(topleft=(x, top_pipe_height + self.pipe_gap))

        # Dummy surface/rect for the base Sprite class (if using sprite groups for collision)
        self.image = pygame.Surface((pipe_width, screen_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, 0))

        self.passed = False # Flag to check if the bird has passed this pipe for scoring

    def update(self):
        # Move the pipes to the left
        self.top_rect.x -= self.scroll_speed
        self.bottom_rect.x -= self.scroll_speed
        self.rect.x -= self.scroll_speed # Update the dummy rect for consistency

    def draw(self, screen):
        # Draw both parts of the pipe on the main screen
        screen.blit(self.top_pipe_image, self.top_rect)
        screen.blit(self.bottom_pipe_image, self.bottom_rect)

        # Draw Outlines
        pygame.draw.rect(screen, DARK_PURPLE, self.top_rect, OUTLINE_THICKNESS)
        pygame.draw.rect(screen, DARK_PURPLE, self.bottom_rect, OUTLINE_THICKNESS)

    def get_pipe_rects(self):
        # Return the actual rectangles for collision detection
        return [self.top_rect, self.bottom_rect]