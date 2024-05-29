import pygame
import random
import pickle
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
PLAYABLE_HEIGHT = HEIGHT - 60  # Leave space for inventory at the bottom
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elysian Grove Adventure")


# Load character images with error handling
def load_image(name):
    try:
        image = pygame.image.load(name)
        return image.convert_alpha()  # Ensure transparency is handled correctly
    except pygame.error as message:
        print(f"Cannot load image: {name}")
        raise SystemExit(message)


# Load images
luminara_img = load_image("luminara.png")
luminara_img = pygame.transform.scale(luminara_img, (45, 45))  # Reduce size by 25%
luminara_invuln_img = pygame.transform.scale(load_image("luminarainvuln.png"), (45, 45))  # Match player size
enemy_img = load_image("enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (45, 45))  # Ensure size matches player size
bossenemy_img = load_image("bossenemy.png")
bossenemy_img = pygame.transform.scale(bossenemy_img, (90, 90))  # Reduce size by 25%
malakar_img = pygame.transform.scale(load_image("malakar.png"), (90, 90))  # Reduce size
background_img = load_image("background.png")

# Load fruit images
gleamberry_img = pygame.transform.scale(load_image("gleamberry.png"), (30, 30))  # Increased by 50%
shimmeringapple_img = pygame.transform.scale(load_image("shimmeringapple.png"), (30, 30))  # Increased by 50%
etherealpear_img = pygame.transform.scale(load_image("etherealpear.png"), (30, 30))  # Increased by 50%
flamefruit_img = pygame.transform.scale(load_image("flamefruit.png"), (30, 30))  # Increased by 50%
moonbeammelon_img = pygame.transform.scale(load_image("moonbeammelon.png"), (30, 30))  # Increased by 50%

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RAINBOW_COLORS = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.default_image = image
        self.invuln_image = luminara_invuln_img
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, PLAYABLE_HEIGHT // 2)
        self.speed = 5
        self.experience = 0
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.inventory = {"Gleam Berry": 0, "Shimmering Apple": 0, "Ethereal Pear": 0, "Flamefruit": 0,
                          "Moonbeam Melon": 0}
        self.damage = 20  # Default damage
        self.invulnerable = False
        self.last_hit = pygame.time.get_ticks()  # Track the last time the player was hit
        self.invuln_end_time = 0  # Track when the invulnerability ends
        self.melon_end_time = 0  # Track when the melon's effect ends
        self.last_regen_time = pygame.time.get_ticks()  # Track the last time health was regenerated
        self.special_attack_ready = True
        self.special_attack_time = 0
        self.flamefruit_end_time = 0
        self.flamefruit_active = False
        self.flamefruit_position = None

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, PLAYABLE_HEIGHT - self.rect.height))

    def collect_fruit(self, fruit):
        self.inventory[fruit.name] += 1
        trigger_rainbow_splash()
        if fruit.name == "Gleam Berry":
            self.health = min(self.health + 10, self.max_health)
        elif fruit.name == "Shimmering Apple":
            self.speed += 1
            self.invulnerable = True
            self.image = self.invuln_image
            self.invuln_end_time = pygame.time.get_ticks() + 3000  # 3 seconds total
        elif fruit.name == "Ethereal Pear":
            self.experience += 150
            self.health = min(self.health + 20, self.max_health + 20)
            self.max_health += 5
        elif fruit.name == "Flamefruit":
            self.experience += 100
            self.flamefruit_end_time = pygame.time.get_ticks() + 3000  # 3 seconds total
            self.flamefruit_active = True
            self.flamefruit_position = fruit.rect.center
        elif fruit.name == "Moonbeam Melon":
            self.experience += 200
            self.damage = 100  # Increase damage by a factor of 5
            self.melon_end_time = pygame.time.get_ticks() + 3050  # 3.05 seconds total

        self.experience += 100
        if self.experience >= 1000:
            self.level += 1
            self.experience = 0
            trigger_level_up_splash()

        return fruit.name

    def attack(self, enemy):
        enemy.health -= self.damage
        trigger_rainbow_splash()
        if enemy.health <= 0:
            enemy.kill()
            self.experience += 50  # Award experience for defeating enemies
            if isinstance(enemy, BossEnemy):
                self.experience += 500  # Award more experience for defeating boss enemies
            if isinstance(enemy, Malakar):
                self.experience += 1000  # Award even more experience for defeating Malakar
                global malakar_spawn_allowed_time
                malakar_spawn_allowed_time = pygame.time.get_ticks() + 15000  # 15 seconds delay before Malakar can respawn

    def take_damage(self, amount):
        if not self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_hit > 1000:  # 1 second cooldown
                self.health -= amount
                self.last_hit = current_time

    def special_attack(self):
        if self.special_attack_ready:
            for sprite in all_sprites:
                if isinstance(sprite, (NightCrawler, BossEnemy, Malakar)):
                    distance = ((self.rect.centerx - sprite.rect.centerx) ** 2 + (
                                self.rect.centery - sprite.rect.centery) ** 2) ** 0.5
                    if distance <= WIDTH // 5:
                        sprite.health -= 250
                        trigger_rainbow_splash()
                        if sprite.health <= 0:
                            sprite.kill()
                            self.experience += 50
                            if isinstance(sprite, BossEnemy):
                                self.experience += 500
                            if isinstance(sprite, Malakar):
                                self.experience += 1000
                                global malakar_spawn_allowed_time
                                malakar_spawn_allowed_time = pygame.time.get_ticks() + 15000  # 15 seconds delay before Malakar can respawn
            self.special_attack_ready = False
            self.special_attack_time = pygame.time.get_ticks() + 30000  # 30 second cooldown

    def update(self):
        current_time = pygame.time.get_ticks()

        # Reset damage after the melon's effect ends
        if current_time > self.melon_end_time:
            self.damage = 20  # Reset to default damage

        # End invulnerability after the duration
        if current_time > self.invuln_end_time:
            self.invulnerable = False
            self.image = self.default_image

        # Health regeneration over time
        if current_time - self.last_regen_time > 5000 and self.health < self.max_health:  # Regenerate every 5 seconds
            self.health += 1
            self.last_regen_time = current_time

        # Special attack cooldown
        if not self.special_attack_ready and current_time > self.special_attack_time:
            self.special_attack_ready = True

        # End flamefruit effect
        if self.flamefruit_active and current_time > self.flamefruit_end_time:
            self.flamefruit_active = False


# Fruit class
class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, name, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.name = name


# Night Crawler class with improved movement
class NightCrawler(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = 100
        self.speed = random.uniform(0.5, 1.5)  # Reduced by half
        self.aggro_radius = WIDTH // 5

    def update(self):
        # Only move towards the player if within aggro radius
        if pygame.sprite.collide_circle_ratio(self.aggro_radius / self.rect.width)(self, player):
            # Smooth, random movement
            if self.rect.x < player.rect.x:
                self.rect.x += self.speed
            elif self.rect.x > player.rect.x:
                self.rect.x -= self.speed
            if self.rect.y < player.rect.y:
                self.rect.y += self.speed
            elif self.rect.y > player.rect.y:
                self.rect.y -= self.speed
            if pygame.sprite.collide_rect(self, player):
                player.take_damage(1)
        elif player.flamefruit_active and player.flamefruit_position:
            # Move towards the location where flamefruit was collected
            if self.rect.x < player.flamefruit_position[0]:
                self.rect.x += self.speed
            elif self.rect.x > player.flamefruit_position[0]:
                self.rect.x -= self.speed
            if self.rect.y < player.flamefruit_position[1]:
                self.rect.y += self.speed
            elif self.rect.y > player.flamefruit_position[1]:
                self.rect.y -= self.speed


# Boss Enemy class
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bossenemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = 500
        self.speed = random.uniform(0.5, 1.5)  # Reduced by half
        self.aggro_radius = WIDTH // 5

    def update(self):
        # Only move towards the player if within aggro radius
        if pygame.sprite.collide_circle_ratio(self.aggro_radius / self.rect.width)(self, player):
            if self.rect.x < player.rect.x:
                self.rect.x += self.speed
            elif self.rect.x > player.rect.x:
                self.rect.x -= self.speed
            if self.rect.y < player.rect.y:
                self.rect.y += self.speed
            elif self.rect.y > player.rect.y:
                self.rect.y -= self.speed
            if pygame.sprite.collide_rect(self, player):
                player.take_damage(10)


# Malakar class
class Malakar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = malakar_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = 5000
        self.speed = random.uniform(0.5, 1.5)  # Reduced by half
        self.aggro_radius = WIDTH // 5

    def update(self):
        # Only move towards the player if within aggro radius
        if pygame.sprite.collide_circle_ratio(self.aggro_radius / self.rect.width)(self, player):
            if self.rect.x < player.rect.x:
                self.rect.x += self.speed
            elif self.rect.x > player.rect.x:
                self.rect.x -= self.speed
            if self.rect.y < player.rect.y:
                self.rect.y += self.speed
            elif self.rect.y > player.rect.y:
                self.rect.y -= self.speed
            if pygame.sprite.collide_rect(self, player):
                player.take_damage(10)


# Additional functions
def trigger_rainbow_splash():
    global rainbow_splash, rainbow_splash_time
    rainbow_splash = True
    rainbow_splash_time = pygame.time.get_ticks()


def draw_rainbow_splash(surface):
    global rainbow_splash
    if rainbow_splash:
        color = random.choice(RAINBOW_COLORS)
        surface.fill(color, special_flags=pygame.BLEND_MULT)
        rainbow_splash = False  # Single frame duration


def trigger_level_up_splash():
    global level_up_splash, level_up_splash_time
    level_up_splash = True
    level_up_splash_time = pygame.time.get_ticks()


def draw_level_up_splash(surface):
    global level_up_splash
    if level_up_splash:
        draw_text(surface, "LEVEL UP!", 50, WIDTH // 2, HEIGHT // 2, GREEN)
        if pygame.time.get_ticks() - level_up_splash_time > 1000:  # Display for 1 second
            level_up_splash = False


def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def draw_inventory(surface, player):
    # Draw the inventory background
    pygame.draw.rect(surface, BLUE, (0, PLAYABLE_HEIGHT, WIDTH, HEIGHT - PLAYABLE_HEIGHT))

    x_offset = 10
    y_offset = PLAYABLE_HEIGHT + 10

    draw_text(surface, f'Collected: {fruit_name}', 30, WIDTH // 2, PLAYABLE_HEIGHT + 10, GREEN)

    # Draw each fruit in the inventory with its count
    for fruit, image in fruit_names_images:
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(player.inventory[fruit]), 18, x_offset + 30, y_offset, WHITE)
        x_offset += 50


def draw_legend(surface):
    legend_text = ["Arrow Keys: Move", "Spacebar: Attack", "N: Special Attack", "P: Pause"]
    x = WIDTH - 150
    y = HEIGHT - 50
    for line in legend_text:
        draw_text(surface, line, 18, x, y, WHITE)
        y += 20


def draw_health_bar(surface, x, y, health, max_health, width, height, border=2):
    if health < 0:
        health = 0
    fill = (health / max_health) * width
    outline_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, RED if health > max_health * 0.1 else WHITE, fill_rect)
    pygame.draw.rect(surface, BLUE, outline_rect, border)


# Custom save and load functions
def save_game():
    with open("savegame.dat", "wb") as f:
        pickle.dump({
            'experience': player.experience,
            'level': player.level,
            'health': player.health,
            'max_health': player.max_health,
            'inventory': player.inventory,
            'damage': player.damage,
            'invulnerable': player.invulnerable,
            'last_hit': player.last_hit,
            'invuln_end_time': player.invuln_end_time,
            'melon_end_time': player.melon_end_time,
            'last_regen_time': player.last_regen_time,
            'special_attack_ready': player.special_attack_ready,
            'special_attack_time': player.special_attack_time,
            'flamefruit_end_time': player.flamefruit_end_time,
            'flamefruit_active': player.flamefruit_active,
            'flamefruit_position': player.flamefruit_position
        }, f)


def load_game():
    global player, all_sprites, fruits, enemies, bossenemies, malakar_group
    if os.path.exists("savegame.dat"):
        with open("savegame.dat", "rb") as f:
            data = pickle.load(f)
            player.experience = data['experience']
            player.level = data['level']
            player.health = data['health']
            player.max_health = data['max_health']
            player.inventory = data['inventory']
            player.damage = data['damage']
            player.invulnerable = data['invulnerable']
            player.last_hit = data['last_hit']
            player.invuln_end_time = data['invuln_end_time']
            player.melon_end_time = data['melon_end_time']
            player.last_regen_time = data['last_regen_time']
            player.special_attack_ready = data['special_attack_ready']
            player.special_attack_time = data['special_attack_time']
            player.flamefruit_end_time = data['flamefruit_end_time']
            player.flamefruit_active = data['flamefruit_active']
            player.flamefruit_position = data['flamefruit_position']
            all_sprites.empty()
            fruits.empty()
            enemies.empty()
            bossenemies.empty()
            malakar_group.empty()
            all_sprites.add(player)


# Create player and groups
player = Player(luminara_img)
all_sprites = pygame.sprite.Group()
fruits = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bossenemies = pygame.sprite.Group()
malakar_group = pygame.sprite.Group()

all_sprites.add(player)

fruit_names_images = [("Gleam Berry", gleamberry_img), ("Shimmering Apple", shimmeringapple_img),
                      ("Ethereal Pear", etherealpear_img), ("Flamefruit", flamefruit_img),
                      ("Moonbeam Melon", moonbeammelon_img)]

# Create initial fruits and enemies
for _ in range(10):  # Increased number of fruits
    name, image = random.choice(fruit_names_images)
    fruit = Fruit(random.randint(0, WIDTH - 30), random.randint(0, PLAYABLE_HEIGHT - 30), name, image)
    fruits.add(fruit)
    all_sprites.add(fruit)

for _ in range(10):  # Increased number of enemies
    enemy = NightCrawler(random.randint(0, WIDTH - 45), random.randint(0, PLAYABLE_HEIGHT - 45))
    enemies.add(enemy)
    all_sprites.add(enemy)

# Main game loop
running = True
paused = False
game_won = False
clock = pygame.time.Clock()

# Timers for spawning
fruit_spawn_time = pygame.time.get_ticks()
enemy_spawn_time = pygame.time.get_ticks()
bossenemy_spawn_time = pygame.time.get_ticks()
malakar_spawn_allowed_time = pygame.time.get_ticks() + 30000  # Malakar spawns after 30 seconds

# Variables for displaying fruit name
show_fruit_name = False
fruit_name = ""
fruit_name_time = 0

# Variables for rainbow splash
rainbow_splash = False
rainbow_splash_time = 0

# Variables for level-up splash
level_up_splash = False
level_up_splash_time = 0


# Main menu
def show_menu():
    screen.fill(BLACK)
    draw_text(screen, "Elysian Grove Adventure", 50, WIDTH // 2, HEIGHT // 4, WHITE)
    draw_text(screen, "Press S to Start", 30, WIDTH // 2, HEIGHT // 2, WHITE)
    draw_text(screen, "Press L to Load Game", 30, WIDTH // 2, HEIGHT // 2 + 40, WHITE)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    waiting = False
                if event.key == pygame.K_l:
                    load_game()
                    waiting = False


show_menu()

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            if event.key == pygame.K_n:
                player.special_attack()
            if event.key == pygame.K_s:
                save_game()

    if not paused and not game_won and player.health > 0:
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1
        player.move(dx, dy)

        # Check for collisions with fruits
        collected_fruits = pygame.sprite.spritecollide(player, fruits, True)
        for fruit in collected_fruits:
            fruit_name = player.collect_fruit(fruit)
            show_fruit_name = True
            fruit_name_time = current_time

        # Check for collisions with enemies
        enemies_hit = pygame.sprite.spritecollide(player, enemies, False)
        bossenemies_hit = pygame.sprite.spritecollide(player, bossenemies, False)
        malakar_hit = pygame.sprite.spritecollide(player, malakar_group, False)
        if keys[pygame.K_SPACE]:
            for enemy in enemies_hit:
                player.attack(enemy)
            for bossenemy in bossenemies_hit:
                player.attack(bossenemy)
            for malakar in malakar_hit:
                player.attack(malakar)

        # Spawn new fruit every 2 seconds
        if current_time - fruit_spawn_time >= 2000:
            name, image = random.choice(fruit_names_images)
            fruit = Fruit(random.randint(0, WIDTH - 30), random.randint(0, PLAYABLE_HEIGHT - 30), name, image)
            fruits.add(fruit)
            all_sprites.add(fruit)
            fruit_spawn_time = current_time

        # Spawn regular enemy every 2 seconds
        if current_time - enemy_spawn_time >= 2000:
            enemy = NightCrawler(random.randint(0, WIDTH - 45), random.randint(0, PLAYABLE_HEIGHT - 45))
            enemies.add(enemy)
            all_sprites.add(enemy)
            enemy_spawn_time = current_time

        # Spawn boss enemy every 5 seconds if fewer than 3 are present
        if len(bossenemies) < 3 and current_time - bossenemy_spawn_time >= 5000:
            bossenemy = BossEnemy(random.randint(0, WIDTH - 90), random.randint(0, PLAYABLE_HEIGHT - 90))
            bossenemies.add(bossenemy)
            all_sprites.add(bossenemy)
            bossenemy_spawn_time = current_time

        # Spawn Malakar if no boss enemies are present and allowed
        if len(bossenemies) == 0 and len(malakar_group) == 0 and current_time > malakar_spawn_allowed_time:
            malakar = Malakar(random.randint(0, WIDTH - 90), random.randint(0, PLAYABLE_HEIGHT - 90))
            malakar_group.add(malakar)
            all_sprites.add(malakar)

        # Update sprites
        all_sprites.update()

    # Draw everything
    screen.blit(background_img, (0, 0))  # Draw the background
    all_sprites.draw(screen)
    draw_rainbow_splash(screen)
    draw_level_up_splash(screen)
    draw_inventory(screen, player)
    draw_legend(screen)

    # Display enemy health as bars above enemy sprites
    for enemy in enemies:
        draw_health_bar(screen, enemy.rect.x, enemy.rect.y - 10, enemy.health, 100, 40, 5)
    for bossenemy in bossenemies:
        draw_health_bar(screen, bossenemy.rect.x, bossenemy.rect.y - 10, bossenemy.health, 500, 40, 5)
    for malakar in malakar_group:
        draw_health_bar(screen, malakar.rect.x, malakar.rect.y - 10, malakar.health, 5000, 40, 5)

    # Display player health as a larger, more prominent bar
    draw_health_bar(screen, player.rect.x - 10, player.rect.y - 15, player.health, player.max_health, 60, 10, 2)

    draw_text(screen, f'Level: {player.level}', 18, 50, 10, WHITE)
    draw_text(screen, f'Experience: {player.experience}', 18, 150, 10, WHITE)
    draw_text(screen, f'Health: {int(player.health)}', 18, 250, 10, WHITE)  # Display health as an integer

    if player.health <= 0:
        draw_text(screen, 'GAME OVER', 50, WIDTH // 2, HEIGHT // 2, RED)
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    if player.level >= 100:
        draw_text(screen, 'YOU WIN', 50, WIDTH // 2, HEIGHT // 2, GREEN)
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
        game_won = True

    if show_fruit_name and current_time - fruit_name_time < 1000:  # Display fruit name for 1 second
        draw_text(screen, f'Collected: {fruit_name}', 30, WIDTH // 2, PLAYABLE_HEIGHT + 10, GREEN)
    else:
        show_fruit_name = False

    if player.invulnerable:
        draw_text(screen, 'Status: Invulnerable', 18, WIDTH // 2, PLAYABLE_HEIGHT + 30, GREEN)
    if player.damage == 100:
        draw_text(screen, 'Status: Increased Damage', 18, WIDTH // 2, PLAYABLE_HEIGHT + 50, GREEN)

    if paused:
        draw_text(screen, 'PAUSED', 50, WIDTH // 2, HEIGHT // 2, BLUE)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
