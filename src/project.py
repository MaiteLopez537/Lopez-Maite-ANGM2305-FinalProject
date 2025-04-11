import pygame
import random
import sys
import math

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
CARBON_GRAY = (50, 50, 50)  # Dark gray for base carborundum color
METALIC_BLUE = (70, 130, 180)  # Light blue for metal sheen
METALIC_GREEN = (0, 255, 255)  # Light greenish shine
SHIMMER_COLOR = (192, 192, 192)  # Silver shimmer for highlights

# Load galaxy background image
background = pygame.image.load('galaxy_background.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load spaceship image
spaceship_image = pygame.image.load('spaceship_image.png')
spaceship_image = pygame.transform.scale(spaceship_image, (80, 80))  # Resize to fit game world

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)  # Bullet color
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
        self.image = spaceship_image
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

# Carborundum rock class (updated with realistic look)
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(45, 65)
        self.image = self.generate_carborundum_surface(self.size)
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 3)
        self.angle = random.randint(0, 360)

    def generate_carborundum_surface(self, size):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)
        num_points = random.randint(7, 11)
        radius = size // 2

        # Base dark gray color for the carborundum
        base_color = CARBON_GRAY

        # Adding some shimmer colors (light blue and greenish highlights)
        shimmer_colors = [METALIC_BLUE, METALIC_GREEN, SHIMMER_COLOR]

        # Build irregular jagged polygon (crystalline facets)
        points = []
        for i in range(num_points):
            angle = math.radians(i * (360 / num_points))
            r = radius + random.randint(-8, 12)
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            points.append((x, y))

        pygame.draw.polygon(surface, base_color, points)

        # Add metallic shimmer for highlights on facets
        for _ in range(random.randint(5, 8)):
            px = random.randint(5, size - 10)
            py = random.randint(5, size - 10)
            shimmer_color = random.choice(shimmer_colors)
            pygame.draw.polygon(surface, shimmer_color, [
                (px, py),
                (px + random.randint(-5, 5), py + random.randint(5, 15)),
                (px + random.randint(-5, 5), py + random.randint(10, 20))
            ])

        # Add some random facets with silver highlights
        for _ in range(random.randint(3, 5)):
            sparkle_x = random.randint(0, size)
            sparkle_y = random.randint(0, size)
            pygame.draw.circle(surface, (255, 255, 255, 90), (sparkle_x, sparkle_y), 2)

        return surface

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)

        self.angle += 2
        if self.angle >= 360:
            self.angle = 0

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def explode(self):
        # Create shards when the rock explodes
        shards = []
        for _ in range(random.randint(5, 10)):
            shard = {
                "pos": pygame.Vector2(self.rect.centerx, self.rect.centery),
                "vel": pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2)),
                "size": random.randint(5, 10),
                "color": random.choice([METALIC_BLUE, METALIC_GREEN, SHIMMER_COLOR]),
            }
            shards.append(shard)
        return shards

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
            score += 10
            bullet.kill()  # Remove the bullet
            rock = Rock()  # Spawn a new rock after collision
            all_sprites.add(rock)
            rocks.add(rock)

            # Explode rock into shards
            shards = hit.explode()
            for shard in shards:
                pygame.draw.circle(screen, shard["color"], (int(shard["pos"].x), int(shard["pos"].y)), shard["size"])

    # Draw everything
    screen.fill(BLACK)
    screen.blit(background, (0, 0))  # Draw the galaxy background

    # Draw all rocks
    for rock in rocks:
        screen.blit(rock.image, rock.rect)

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
