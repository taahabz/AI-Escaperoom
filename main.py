import pygame
import json
import random
from ai import initialize_ai  # Import the AI class
import random
import time

# Initialize pygame
pygame.init()
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)
# Screen dimensions

pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)

# Screen dimensions
GAME_DURATION = 100
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 700
TILE_SIZE = 8
SCALE_FACTOR = 3
SCALED_TILE_SIZE = TILE_SIZE * SCALE_FACTOR

# Game speeds
player_speed = 1  # Base player speed
enemy_speed = 0.5  # Half of player speed

# Load assets
agent_image = pygame.image.load("assets/agent.png")
tileset_image = pygame.image.load("assets/tileset.png")
ai_actions = []
start_time = time.time()

# Scale assets
agent_image = pygame.transform.scale(agent_image, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))

# Levels and map data
level_files = ["assets/lvl1.json", "assets/lvl2.json", "assets/lvl3.json", "assets/lvl4.json", "assets/lvl5.json"]
levels = [json.load(open(file)) for file in level_files]

# Game state variables
game_won = False
game_over = False

def calculate_game_accuracy():
    # Movement efficiency
    total_moves = len(ai_actions)
    if total_moves == 0:
        return 0.0
        
    # Track successful moves (not hitting walls/hazards)
    successful_moves = sum(1 for action in ai_actions 
                         if "collision" not in str(action) and "reset" not in str(action))
    movement_score = (successful_moves / total_moves) * 100
    
    # Level progression score
    level_score = (current_level_index / len(levels)) * 100
    
    # Key collection rate
    total_keys = sum(len(level["keys"]) for level in [parse_level(level) for level in levels[:current_level_index + 1]])
    keys_collected = total_keys - len(collected_keys) if total_keys > 0 else 0
    key_score = (keys_collected / max(total_keys, 1)) * 100
    
    # Time efficiency score
    time_score = max(0, 100 - (int(time.time() - start_time) / GAME_DURATION * 100))
    
    # Weighted accuracy calculation
    weights = {
        'movement': 0.35,
        'level': 0.25,
        'keys': 0.25,
        'time': 0.15
    }
    
    final_accuracy = (
        movement_score * weights['movement'] +
        level_score * weights['level'] +
        key_score * weights['keys'] +
        time_score * weights['time']
    )
    
    return min(max(final_accuracy, 0), 100)

def display_game_summary():
    # Colors
    BACKGROUND = (28, 28, 30)
    TEXT_PRIMARY = (240, 240, 245)
    TEXT_SECONDARY = (199, 199, 204)
    ACCENT_SUCCESS = (48, 209, 88)
    ACCENT_FAILURE = (255, 69, 58)
    ACCENT_INFO = (100, 210, 255)
    
    screen.fill(BACKGROUND)
    
    # Header
    header_height = 80
    pygame.draw.rect(screen, (38, 38, 40), (0, 0, SCREEN_WIDTH, header_height))
    header_font = pygame.font.Font(None, 48)
    outcome_text = "MISSION ACCOMPLISHED" if game_won else "MISSION FAILED"
    text = header_font.render(outcome_text, True, ACCENT_SUCCESS if game_won else ACCENT_FAILURE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, header_height // 2))
    screen.blit(text, text_rect)
    
    y_pos = header_height + 40
    
    # AI Performance section
    title_font = pygame.font.Font(None, 36)
    text = title_font.render("AI Performance Metrics", True, ACCENT_INFO)
    screen.blit(text, (50, y_pos))
    y_pos += 50
    
    # Animated accuracy bar
    accuracy = calculate_game_accuracy()
    bar_width = 600
    bar_height = 30
    border_radius = 15
    
    # Animation
    steps = 60
    for i in range(steps + 1):
        current_acc = (accuracy * i) / steps
        fill_width = int((bar_width * current_acc) / 100)
        
        # Background bar
        pygame.draw.rect(screen, (58, 58, 60),
                        (50, y_pos, bar_width, bar_height),
                        border_radius=border_radius)
        
        # Animated fill
        if fill_width > 0:
            pygame.draw.rect(screen, ACCENT_INFO,
                           (50, y_pos, fill_width, bar_height),
                           border_radius=border_radius)
        
        text = title_font.render(f"Accuracy: {current_acc:.1f}%", True, TEXT_PRIMARY)
        pygame.draw.rect(screen, BACKGROUND, (670, y_pos, 200, bar_height))
        screen.blit(text, (670, y_pos))
        
        pygame.display.flip()
        pygame.time.wait(16)
    
    y_pos += 60
    
    # Stats section
    stats_font = pygame.font.Font(None, 32)
    stats = [
        ("Total Actions", len(ai_actions)),
        ("Time Played", f"{int(time.time() - start_time)}s"),
        ("Levels Completed", current_level_index)
    ]
    
    for stat, value in stats:
        text = stats_font.render(f"{stat}: {value}", True, TEXT_SECONDARY)
        screen.blit(text, (50, y_pos))
        y_pos += 40
    
    # Action breakdown
    y_pos += 20
    text = title_font.render("Action Distribution", True, ACCENT_INFO)
    screen.blit(text, (50, y_pos))
    y_pos += 40
    
    action_counts = {}
    for action_data in ai_actions:
        action = action_data["action"]
        action_counts[action] = action_counts.get(action, 0) + 1
    
    for action, count in action_counts.items():
        text = stats_font.render(f"{action}: {count}", True, TEXT_SECONDARY)
        screen.blit(text, (50, y_pos))
        y_pos += 30
    
    pygame.display.flip()
    
    # Display duration
    end_time = time.time() + 300
    while time.time() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        pygame.time.wait(100)
# Helper function to extract and scale a tile from the tileset
def get_tile_image(tile_id, tileset, tile_size, tiles_per_row, scale_factor):
    if tile_id == 0:
        return None
    tile_id -= 1  # Adjust for 0-indexing
    x = (tile_id % tiles_per_row) * tile_size
    y = (tile_id // tiles_per_row) * tile_size
    tile = tileset.subsurface((x, y, tile_size, tile_size))
    return pygame.transform.scale(tile, (tile_size * scale_factor, tile_size * scale_factor))

# Parse a single level
def parse_level(level):
    tiles_per_row = level["tilesets"][0]["columns"]
    layers = {layer["name"]: layer for layer in level["layers"]}
    walls = set()
    spikes = set()
    enemies = set()  # To store enemy positions
    keys = {}
    doors = []
    start_pos = None

    # Process layers
    for layer_name, layer in layers.items():
        for i, tile_id in enumerate(layer["data"]):
            if tile_id == 0:
                continue

            x = i % level["width"]
            y = i // level["width"]

            if layer_name == "walls":
                walls.add((x, y))
            elif layer_name == "spikes":
                spikes.add((x, y))
            elif layer_name == "enemies":
                if current_level_index in [3, 4]:
                    enemies.add((x, y, tile_id))  # Store enemy type with position
            elif layer_name == "keys":
                keys[(x, y)] = tile_id
            elif layer_name == "door":
                doors.append((x, y, tile_id))
            elif layer_name == "player" and start_pos is None:
                start_pos = (x, y)

    return {
        "walls": walls,
        "spikes": spikes,
        "enemies": enemies,
        "keys": keys,
        "doors": doors,
        "start_pos": start_pos,
        "width": level["width"],
        "height": level["height"],
        "tiles_per_row": tiles_per_row,
        "layers": layers,
    }

# Function to move enemies with rule-based AI
def move_enemy(enemy_pos, level_data, player_rect):
    enemy_x, enemy_y, tile_id = enemy_pos
    player_tile_x = player_rect.x // SCALED_TILE_SIZE
    player_tile_y = player_rect.y // SCALED_TILE_SIZE
    
    # Calculate distance to player
    dx = player_tile_x - enemy_x
    dy = player_tile_y - enemy_y
    
    # Detection range (how far the enemy can "see" the player)
    detection_range = 5
    
    # If player is within detection range, move towards them
    if abs(dx) + abs(dy) < detection_range:
        small_step = 0.3
        # Move horizontally
        if abs(dx) > 0.1:
            enemy_x += small_step if dx > 0 else -small_step
        # Move vertically
        if abs(dy) > 0.1:
            enemy_y += small_step if dy > 0 else -small_step
    else:
        # Random patrol behavior when player is not detected
        direction = random.choice(['up', 'down', 'left', 'right'])
        small_step = 0.3
        
        if direction == 'up':
            enemy_y -= small_step
        elif direction == 'down':
            enemy_y += small_step
        elif direction == 'left':
            enemy_x -= small_step
        elif direction == 'right':
            enemy_x += small_step
    
    # Keep enemy within bounds
    enemy_x = max(0, min(level_data["width"] - 0.1, enemy_x))
    enemy_y = max(0, min(level_data["height"] - 0.1, enemy_y))
    
    return (enemy_x, enemy_y, tile_id)

# Initialize the first level
current_level_index = 0
current_level_data = parse_level(levels[current_level_index])

# Game variables
collected_keys = current_level_data["keys"].copy()  # Tracks collected keys
has_key = False if collected_keys else True  # Automatically unlock doors if no keys exist
player_rect = pygame.Rect(
    current_level_data["start_pos"][0] * SCALED_TILE_SIZE,
    current_level_data["start_pos"][1] * SCALED_TILE_SIZE,
    SCALED_TILE_SIZE,
    SCALED_TILE_SIZE,
)
camera_x = 0

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Escape Room")

# Function to reset the level
def reset_level():
    global player_rect, has_key, collected_keys
    print("You hit a hazard! Restarting level...")
    player_rect.x = current_level_data["start_pos"][0] * SCALED_TILE_SIZE
    player_rect.y = current_level_data["start_pos"][1] * SCALED_TILE_SIZE
    collected_keys = current_level_data["keys"].copy()  # Reset keys
    has_key = False if collected_keys else True  # Reset key status dynamically

# Function to check if the new position collides with walls or doors
def check_collision(player_rect, walls, doors, has_key):
    # Check walls
    for wall_x, wall_y in walls:
        wall_rect = pygame.Rect(wall_x * SCALED_TILE_SIZE, wall_y * SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE)
        if player_rect.colliderect(wall_rect):
            return True
    # Check doors
    for door_x, door_y, _ in doors:
        if not has_key:  # Only block if the player doesn't have the key
            door_rect = pygame.Rect(
                door_x * SCALED_TILE_SIZE, door_y * SCALED_TILE_SIZE, SCALED_TILE_SIZE, SCALED_TILE_SIZE
            )
            if player_rect.colliderect(door_rect):
                return True
    return False

# Game loop
def check_time():
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, GAME_DURATION - elapsed_time)
    
    # Draw timer fp
    timer_text = font.render(f"Time: {int(remaining_time)}s", True, (255, 255, 255))
    screen.blit(timer_text, (10, 10))
    
    return remaining_time <= 0


# Initialize the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Escape Room")
clock = pygame.time.Clock()

current_level_index = 0
current_level_data = parse_level(levels[current_level_index])
collected_keys = current_level_data["keys"].copy()
has_key = False if collected_keys else True
player_rect = pygame.Rect(
    current_level_data["start_pos"][0] * SCALED_TILE_SIZE,
    current_level_data["start_pos"][1] * SCALED_TILE_SIZE,
    SCALED_TILE_SIZEc cx cxdscas    ,
    SCALED_TILE_SIZE
)
camera_x = 0

# Initialize AI agent
ai_agent = initialize_ai()
ai_control = False

# Game loop
running = True
while running:
    # Check timer
    if check_time():
        print("Time's up! Game Over!")
        game_won = False 
        display_game_summary()
        running = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                ai_control = not ai_control

    # Get player movement
    dx, dy = 0, 0
    if ai_control:
        action = ai_agent.update({
            "player_rect": player_rect,
            "current_level_data": current_level_data,
            "collected_keys": collected_keys,
            "has_key": has_key
        })
        ai_actions.append({
            "time": time.time() - start_time,
            "action": action,
            "position": (player_rect.x // SCALED_TILE_SIZE, player_rect.y // SCALED_TILE_SIZE)
        })
        if action == 'up': dy = -player_speed
        elif action == 'down': dy = player_speed
        elif action == 'left': dx = -player_speed
        elif action == 'right': dx = player_speed
    else:
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP]: dy = -player_speed
        if keys_pressed[pygame.K_DOWN]: dy = player_speed
        if keys_pressed[pygame.K_LEFT]: dx = -player_speed
        if keys_pressed[pygame.K_RIGHT]: dx = player_speed

    # Update player position
    new_rect = player_rect.move(dx * SCALED_TILE_SIZE, dy * SCALED_TILE_SIZE)
    if not check_collision(new_rect, current_level_data["walls"], current_level_data["doors"], has_key):
        player_rect = new_rect

    # Check key collection
    player_tile = (player_rect.x // SCALED_TILE_SIZE, player_rect.y // SCALED_TILE_SIZE)
    if player_tile in collected_keys:
        has_key = True
        del collected_keys[player_tile]
        print("Key collected!")

    # Check spike collision
    if player_tile in current_level_data["spikes"]:
        reset_level()

    # Update and check enemy collisions
    updated_enemies = set()
    for enemy_pos in current_level_data["enemies"]:
        new_pos = move_enemy(enemy_pos, current_level_data, player_rect)
        updated_enemies.add(new_pos)
        
        enemy_rect = pygame.Rect(   
            new_pos[0] * SCALED_TILE_SIZE,
            new_pos[1] * SCALED_TILE_SIZE,
            SCALED_TILE_SIZE,
            SCALED_TILE_SIZE
        )
        if player_rect.colliderect(enemy_rect):
            reset_level()
    
    current_level_data["enemies"] = updated_enemies

    # Check door interaction
    for door_pos in current_level_data["doors"]:
        if player_tile == (door_pos[0], door_pos[1]):
            if has_key:
                print("Door unlocked! Moving to next level...")
                current_level_index += 1
                if current_level_index >= len(levels):
                    print("You completed all levels!")
                    game_won = True
                    display_game_summary()
                    running = False
                else:
                    current_level_data = parse_level(levels[current_level_index])
                    reset_level()
            else:
                print("Find the key first!")

    # Draw game
    screen.fill((0, 0, 0))
    
    # Draw level elements
    for layer_name, layer in current_level_data["layers"].items():
        if layer_name in ["player", "keys", "door"]:
            continue
        for i, tile_id in enumerate(layer["data"]):
            if tile_id == 0:
                continue
            x = i % current_level_data["width"]
            y = i // current_level_data["width"]
            tile_image = get_tile_image(tile_id, tileset_image, TILE_SIZE, current_level_data["tiles_per_row"], SCALE_FACTOR)
            if tile_image:
                screen.blit(tile_image, (x * SCALED_TILE_SIZE - camera_x, y * SCALED_TILE_SIZE))

    # Draw remaining elements
    for spike_pos in current_level_data["spikes"]:
        spike_image = get_tile_image(89, tileset_image, TILE_SIZE, current_level_data["tiles_per_row"], SCALE_FACTOR)
        if spike_image:
            screen.blit(spike_image, (spike_pos[0] * SCALED_TILE_SIZE - camera_x, spike_pos[1] * SCALED_TILE_SIZE))

    for enemy_pos in current_level_data["enemies"]:
        enemy_image = get_tile_image(enemy_pos[2], tileset_image, TILE_SIZE, current_level_data["tiles_per_row"], SCALE_FACTOR)
        if enemy_image:
            screen.blit(enemy_image, (enemy_pos[0] * SCALED_TILE_SIZE - camera_x, enemy_pos[1] * SCALED_TILE_SIZE))

    for key_pos, tile_id in collected_keys.items():
        key_image = get_tile_image(tile_id, tileset_image, TILE_SIZE, current_level_data["tiles_per_row"], SCALE_FACTOR)
        if key_image:
            screen.blit(key_image, (key_pos[0] * SCALED_TILE_SIZE - camera_x, key_pos[1] * SCALED_TILE_SIZE))

    for door_pos in current_level_data["doors"]:
        door_tile_id = door_pos[2] if not has_key else 0
        door_image = get_tile_image(door_tile_id, tileset_image, TILE_SIZE, current_level_data["tiles_per_row"], SCALE_FACTOR)
        if door_image:
            screen.blit(door_image, (door_pos[0] * SCALED_TILE_SIZE - camera_x, door_pos[1] * SCALED_TILE_SIZE))

    screen.blit(agent_image, (player_rect.x - camera_x, player_rect.y))

    pygame.display.flip()
    clock.tick(30)
    

pygame.quit()