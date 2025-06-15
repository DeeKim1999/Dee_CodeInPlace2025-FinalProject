import pygame

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, assets_path):
        super().__init__()

        # --- Bird Visual ---
        self.original_image = None
        try:
            # Attempt to load the bird image (e.g., 'dee_red_bird.png' from your 'dee_assets' folder)
            self.original_image = pygame.image.load(f"{assets_path}/dee_red_bird.png").convert_alpha()
            # Scale the image to a suitable size
            self.original_image = pygame.transform.scale(self.original_image, (34, 24))
        except pygame.error:
            print("Warning: dee_red_bird.png not found or could not be loaded. Using a placeholder rectangle.")
            # If image loading fails, create a simple red rectangle as a placeholder
            self.original_image = pygame.Surface((34, 24), pygame.SRCALPHA)
            self.original_image.fill((255, 0, 0, 200)) # Red color with some transparency
            pygame.draw.circle(self.original_image, (255, 255, 0), (17, 12), 8) # Add a yellow "eye"

        self.image = self.original_image # This is the image that will be drawn
        self.rect = self.image.get_rect(center=(x, y)) # Get the rectangle that encloses the image

        # --- Bird Physics ---
        self.gravity = 0.25 # How fast the bird accelerates downwards
        self.flap_strength = -5.5 # Adjusted: Slightly weaker upward velocity for smoother control
        self.velocity = 0 # Current vertical velocity of the bird

    def flap(self):
        # Set upward velocity when the player flaps
        self.velocity = self.flap_strength

    def update(self):
        # Apply gravity to velocity
        self.velocity += self.gravity
        # Limit downward velocity (prevents bird from getting too fast)
        if self.velocity > 8: # Max downward speed
            self.velocity = 8

        # Update bird's vertical position based on velocity
        self.rect.y += self.velocity

        # Rotate the bird image based on its velocity for visual effect
        self.image = pygame.transform.rotozoom(self.original_image, -self.velocity * 3, 1)

    def draw(self, screen):
        # Draw the bird on the screen at its current rectangle position
        screen.blit(self.image, self.rect)