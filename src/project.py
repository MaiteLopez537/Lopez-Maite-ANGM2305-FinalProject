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
CARBON_GRAY = (50, 50, 50)
METALIC_BLUE = (70, 130, 180)
METALIC_GREEN = (0, 255, 255)
SHIMMER_COLOR = (192, 192, 192)

# Load galaxy background image
background = pygame.image.load('galaxy_background.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load spaceship image
spaceship_image = pygame.image.load('spaceship_image.png')
spaceship_image = pygame.transform.scale(spaceship_image, (120, 120))  # Bigger ship

# Health setup
max_health = 10
heart_size = 20

# Function to draw hearts
def draw_heart(surface, x, y, size, color):
    top_curve_radius = size // 4
    triangle_height = size // 1.5
    points = [
        (x, y + top_curve_radius),
        (x - size // 2, y + top_curve_radius),
        (x, y - triangle_height // 3),
        (x + size // 2, y + top_curve_radius)
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.circle(surface, color, (x - top_curve_radius, y), top_curve_radius)
    pygame.draw.circle(surface, color, (x + top_curve_radius, y), top_curve_radius)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
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

# Rock class
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
        points = []
        for i in range(num_points):
            angle = math.radians(i * (360 / num_points))
            r = radius + random.randint(-8, 12)
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            points.append((x, y))

        pygame.draw.polygon(surface, CARBON_GRAY, points)

        for _ in range(random.randint(5, 8)):
            px = random.randint(5, size - 10)
            py = random.randint(5, size - 10)
            shimmer_color = random.choice([METALIC_BLUE, METALIC_GREEN, SHIMMER_COLOR])
            pygame.draw.polygon(surface, shimmer_color, [
                (px, py),
                (px + random.randint(-5, 5), py + random.randint(5, 15)),
                (px + random.randint(-5, 5), py + random.randint(10, 20))
            ])

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

# Game Over screen
def game_over_screen():
    font_large = pygame.font.SysFont("Arial", 64)
    font_small = pygame.font.SysFont("Arial", 32)
    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)

    while True:
        screen.fill(BLACK)
        screen.blit(background, (0, 0))

        # Display "You Died"
        game_over_text = font_large.render("You Died", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))

        # Draw button
        pygame.draw.rect(screen, LIGHT_BLUE, button_rect)
        try_again_text = font_small.render("Try Again", True, BLACK)
        screen.blit(try_again_text, (button_rect.centerx - try_again_text.get_width()//2,
                                     button_rect.centery - try_again_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return

# Start game loop
def start_game():
    global all_sprites, spaceship, bullets, rocks

    current_health = max_health
    score = 0
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    spaceship = Spaceship()
    all_sprites.add(spaceship)

    bullets = pygame.sprite.Group()
    rocks = pygame.sprite.Group()

    for _ in range(10):
        rock = Rock()
        all_sprites.add(rock)
        rocks.add(rock)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                spaceship.shoot()

        all_sprites.update()

        for bullet in bullets:
            rock_hits = pygame.sprite.spritecollide(bullet, rocks, True)
            for hit in rock_hits:
                score += 10
                bullet.kill()
                new_rock = Rock()
                all_sprites.add(new_rock)
                rocks.add(new_rock)
                for shard in hit.explode():
                    pygame.draw.circle(screen, shard["color"], (int(shard["pos"].x), int(shard["pos"].y)), shard["size"])

        rock_hits_player = pygame.sprite.spritecollide(spaceship, rocks, True)
        for hit in rock_hits_player:
            current_health -= 1
            if current_health <= 0:
                game_over_screen()
                return start_game()
            new_rock = Rock()
            all_sprites.add(new_rock)
            rocks.add(new_rock)

        screen.fill(BLACK)
        screen.blit(background, (0, 0))

        for rock in rocks:
            screen.blit(rock.image, rock.rect)

        all_sprites.draw(screen)

        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        for i in range(current_health):
            draw_heart(screen, 30 + i * (heart_size + 5), HEIGHT - 40, heart_size, RED)

        pygame.display.flip()
        clock.tick(60)

# Start the game for the first time
start_game()




