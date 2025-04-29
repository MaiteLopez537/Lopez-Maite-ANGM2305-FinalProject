import pygame
import random
import sys
import math

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

# Load background
background = pygame.image.load('galaxy_background.jpeg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load images with white background removed
def load_transparent_image(path, size=None):
    image = pygame.image.load(path).convert()
    image.set_colorkey(WHITE)  # Make white transparent
    if size:
        image = pygame.transform.scale(image, size)
    return image

# Load spaceship and mothership
spaceship_image = load_transparent_image('spaceship_image.jpeg', (120, 120))
alien_mothership_image = load_transparent_image("alien_mothership.jpeg", (160, 160))

# Health setup
max_health = 10
heart_size = 15

def draw_heart(surface, x, y, size, color):
    top_radius = size // 2
    heart_surface = pygame.Surface((size * 1.5, size * 1.5), pygame.SRCALPHA)
    pygame.draw.circle(heart_surface, color, (top_radius, top_radius), top_radius)
    pygame.draw.circle(heart_surface, color, (top_radius * 2, top_radius), top_radius)
    points = [
        (0, top_radius),
        (top_radius * 1.5, size * 1.5),
        (top_radius * 3, top_radius),
    ]
    pygame.draw.polygon(heart_surface, color, points)
    surface.blit(heart_surface, (x - size // 2, y - size // 2))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class BossLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = spaceship_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
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

class AlienMothership(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = alien_mothership_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))
        self.health = 20
        self.laser_timer = 0
        self.speed_x = 3

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1
        time_now = pygame.time.get_ticks() / 500
        zigzag_offset = math.sin(time_now) * 10
        self.rect.y = 100 + zigzag_offset
        self.laser_timer += 1
        if self.laser_timer > 60:
            self.laser_timer = 0
            for offset in [-30, 0, 30]:
                laser = BossLaser(self.rect.centerx + offset, self.rect.bottom)
                all_sprites.add(laser)
                boss_lasers.add(laser)

    def draw_health_bar(self, surface):
        bar_width = 100
        bar_height = 10
        fill = (self.health / 20) * bar_width
        outline_rect = pygame.Rect(self.rect.centerx - bar_width // 2, self.rect.top - 20, bar_width, bar_height)
        fill_rect = pygame.Rect(outline_rect.x, outline_rect.y, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

def game_over_screen():
    font_large = pygame.font.SysFont("Copperplate", 64)
    font_small = pygame.font.SysFont("Times New Roman", 32)
    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
    while True:
        screen.fill(BLACK)
        screen.blit(background, (0, 0))
        game_over_text = font_large.render("You Died", True, YELLOW)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        try_again_text = font_small.render("Try Again", True, (230, 230, 250))
        screen.blit(try_again_text, (button_rect.centerx - try_again_text.get_width()//2, button_rect.centery - try_again_text.get_height()//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return

def win_screen():
    font_large = pygame.font.SysFont("Copperplate", 64)
    font_small = pygame.font.SysFont("Times New Roman", 32)
    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
    while True:
        screen.fill(BLACK)
        screen.blit(background, (0, 0))
        win_text = font_large.render("You Win!", True, GREEN)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 100))
        try_again_text = font_small.render("Play Again", True, (230, 230, 250))
        screen.blit(try_again_text, (button_rect.centerx - try_again_text.get_width()//2, button_rect.centery - try_again_text.get_height()//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return

def start_game():
    global all_sprites, spaceship, bullets, rocks, boss_lasers
    current_health = max_health
    score = 0
    rock_hits = 0
    boss_fight = False
    boss = None
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    boss_lasers = pygame.sprite.Group()

    spaceship = Spaceship()
    all_sprites.add(spaceship)

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

        if pygame.sprite.spritecollide(spaceship, rocks, True):
            current_health -= 1
            if current_health <= 0:
                game_over_screen()
                return start_game()
            rock = Rock()
            all_sprites.add(rock)
            rocks.add(rock)

        if not boss_fight:
            for bullet in bullets:
                hits = pygame.sprite.spritecollide(bullet, rocks, True)
                for rock in hits:
                    rock_hits += 1
                    score += 10
                    bullet.kill()
                    new_rock = Rock()
                    all_sprites.add(new_rock)
                    rocks.add(new_rock)
                    for shard in rock.explode():
                        pygame.draw.circle(screen, shard["color"], (int(shard["pos"].x), int(shard["pos"].y)), shard["size"])
            if rock_hits >= 10:
                boss_fight = True
                for r in rocks:
                    r.kill()
                boss = AlienMothership()
                all_sprites.add(boss)
        else:
            for bullet in bullets:
                if pygame.sprite.collide_rect(bullet, boss):
                    bullet.kill()
                    boss.health -= 1
                    if boss.health <= 0:
                        win_screen()
                        return start_game()
            if pygame.sprite.spritecollide(spaceship, boss_lasers, True):
                current_health -= 1
                if current_health <= 0:
                    game_over_screen()
                    return start_game()

        screen.fill(BLACK)
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        if boss_fight and boss:
            boss.draw_health_bar(screen)

        font = pygame.font.SysFont("Times New Roman", 24)
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        for i in range(current_health):
            draw_heart(screen, 20 + i * (heart_size + 8), HEIGHT - 30, heart_size, RED)

        pygame.display.flip()
        clock.tick(60)

start_game()









