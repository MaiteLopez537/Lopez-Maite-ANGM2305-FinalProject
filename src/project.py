import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Load galaxy background image
background = pygame.image.load('galaxy_background.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load rock image and remove the white background (if needed)
rock_image = pygame.image.load('rock_image.png')  # Replace with your rock image

def remove_white_background(image):
    image = image.convert_alpha()  # Ensure image has an alpha channel (transparency)
    width, height = image.get_size()
    for y in range(height):
        for x in range(width):
            color = image.get_at((x, y))  # Get RGBA value of each pixel
            if color == WHITE:  # If pixel is white, make it transparent
                image.set_at((x, y), (0, 0, 0, 0))
    return image

rock_image = remove_white_background(rock_image)
rock_image = pygame.transform.scale(rock_image, (50, 50))  # Resize to fit game world

# Load spaceship image and remove the white background (if needed)
spaceship_image = pygame.image.load('spaceship.png')  # Replace with your spaceship image filename
spaceship_image = remove_white_background(spaceship_image)
spaceship_image = pygame.transform.scale(spaceship_image, (80, 80))  # Resize to fit game world

# Pixel Explosion class to simulate explosive pixel effect with new colors
class PixelExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.particles = []  # List of particles that will form the explosion
        self.lifetime = 30  # How long the explosion lasts
        for _ in range(50):  # Create 50 particles
            particle = {
                "pos": pygame.Vector2(x, y),
                "vel": pygame.Vector2(random.uniform(-3, 3), random.uniform(-3, 3)),  # Random velocity for each particle
                "color": random.choice([RED, ORANGE, YELLOW]),  # Random color for each particle (Red, Orange, Yellow)
                "size": random.randint(2, 5),  # Random size of the particle
                "alpha": 255  # Full opacity at the start
            }
            self.particles.append(particle)

    def update(self):
        # Update particles and check for their lifetime
        for particle in self.particles:
            particle["pos"] += particle["vel"]  # Move particle
            particle["alpha"] -= 10  # Fade out particle
            if particle["alpha"] <= 0:  # Remove the particle if it's too transparent
                self.particles.remove(particle)

    def draw(self, surface):
        # Draw each particle as a small rectangle (pixel effect)
        for particle in self.particles:
            pygame.draw.rect(surface, particle["color"], (particle["pos"].x, particle["pos"].y, particle["size"], particle["size"]))
            # Apply alpha to simulate fading
            surface.set_at((int(particle["pos"].x), int(particle["pos"].y)), (particle["color"][0], particle["color"][1], particle["color"][2], particle["alpha"]))

# Rock class (used as the enemy)
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = rock_image
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 3)
        self.angle = random.randint(0, 360)  # Start with random rotation angle

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
        
        # Rotate the rock image
        self.angle += 2  # Increase angle to make the rock rotate
        if self.angle >= 360:  # Reset angle after full rotation
            self.angle = 0
        
        # Rotate the image and keep it centered
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)  # Change bullet color to red
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = spaceship_image  # Use the spaceship image with the transparent background
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 60)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Set up sprite groups
all_sprites = pygame.sprite.Group()
spaceship = Spaceship()
all_sprites.add(spaceship)

bullets = pygame.sprite.Group()
rocks = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Create rocks (enemies)
for i in range(10):
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)

# Game loop
running = True
clock = pygame.time.Clock()
score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                spaceship.shoot()

    # Update all sprites
    all_sprites.update()

    # Check for bullet collisions with rocks
    for bullet in bullets:
        rock_hits = pygame.sprite.spritecollide(bullet, rocks, True)
        for hit in rock_hits:
            # Add an explosion with the pixel effect at the location of the collision
            explosion = PixelExplosion(hit.rect.centerx, hit.rect.centery)
            explosions.add(explosion)
            score += 10
            bullet.kill()  # Remove the bullet
            rock = Rock()  # Spawn a new rock after collision
            all_sprites.add(rock)
            rocks.add(rock)

    # Draw everything
    screen.fill(BLACK)
    screen.blit(background, (0, 0))  # Draw the galaxy background

    # Manually draw explosions
    for explosion in explosions:
        explosion.update()
        explosion.draw(screen)

    # Draw all other sprites
    all_sprites.draw(screen)

    # Display score
    font = pygame.font.SysFont("Arial", 24)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
