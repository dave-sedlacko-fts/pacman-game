"""
Pacman Game - Simple movement version
"""

import pygame
import random
import json
import math
from pathlib import Path

pygame.init()

# Constants
TILE_SIZE = 24
MAZE_WIDTH = 28
MAZE_HEIGHT = 31
GAME_WIDTH = TILE_SIZE * MAZE_WIDTH
GAME_HEIGHT = TILE_SIZE * MAZE_HEIGHT + 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (33, 33, 222)
WALL_BLUE = (33, 33, 150)
PELLET_COLOR = (255, 184, 151)
POWER_PELLET_COLOR = (255, 184, 151)
GHOST_VULNERABLE = (33, 33, 222)
GHOST_FLASH = (255, 255, 255)

PACMAN_COLORS = {
    'yellow': (255, 255, 0),
    'blue': (0, 191, 255),
    'pink': (255, 105, 180),
    'purple': (148, 0, 211),
    'green': (50, 205, 50)
}

GHOST_COLORS = {
    'blinky': (255, 0, 0),
    'pinky': (255, 184, 222),
    'inky': (0, 255, 222),
    'clyde': (255, 184, 82)
}

MAZE_LAYOUT = [
    "1111111111111111111111111111",
    "1222222222222112222222222221",
    "1211112111112112111112111121",
    "1311112111112112111112111131",
    "1211112111112112111112111121",
    "1222222222222222222222222221",
    "1211112112111111112112111121",
    "1211112112111111112112111121",
    "1222222112222112222112222221",
    "1111112111110110111112111111",
    "0000012111110110111112100000",
    "0000012110000000001112100000",
    "0000012110111411110112100000",
    "1111112110100000010112111111",
    "0000002000100000010002000000",
    "1111112110100000010112111111",
    "0000012110111111110112100000",
    "0000012110000000001112100000",
    "0000012110111111110112100000",
    "1111112110111111110112111111",
    "1222222222222112222222222221",
    "1211112111112112111112111121",
    "1311112111112112111112111131",
    "1222112222222002222222112221",
    "1112112112111111112112112111",
    "1112112112111111112112112111",
    "1222222112222112222112222221",
    "1211111111112112111111111121",
    "1211111111112112111111111121",
    "1222222222222222222222222221",
    "1111111111111111111111111111",
]


class HighScoreManager:
    def __init__(self):
        self.scores_file = Path(__file__).parent / "highscores.json"
        self.scores = self.load_scores()

    def load_scores(self):
        if self.scores_file.exists():
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_scores(self):
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except:
            pass

    def add_score(self, name, score):
        self.scores.append({'name': name, 'score': score})
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]
        self.save_scores()

    def is_high_score(self, score):
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]['score']

    def get_scores(self):
        return self.scores


class Pacman:
    def __init__(self, start_x, start_y, color):
        self.start_x = start_x
        self.start_y = start_y
        self.color = color
        self.speed = 4  # Pixels per frame
        self.reset()

    def reset(self):
        # Current tile position
        self.tile_x = self.start_x
        self.tile_y = self.start_y
        # Pixel position (center of current tile)
        self.x = self.tile_x * TILE_SIZE + TILE_SIZE // 2
        self.y = self.tile_y * TILE_SIZE + TILE_SIZE // 2
        # Target tile (where we're moving to)
        self.target_x = self.tile_x
        self.target_y = self.tile_y
        # Direction for display
        self.face_dir = (0, 0)
        # Is Pacman currently moving between tiles?
        self.moving = False
        # Buffered input
        self.input_dir = (0, 0)
        # Animation
        self.mouth_open = True
        self.anim_timer = 0

    def request_direction(self, dx, dy):
        """Player requests a direction."""
        self.input_dir = (dx, dy)

    def is_walkable(self, maze, tx, ty):
        """Check if tile is walkable."""
        # Tunnel wrap
        if tx < 0:
            tx = MAZE_WIDTH - 1
        elif tx >= MAZE_WIDTH:
            tx = 0
        if ty < 0 or ty >= MAZE_HEIGHT:
            return False
        cell = maze[ty][tx]
        return cell != 1 and cell != 4

    def update(self, maze):
        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 5:
            self.anim_timer = 0
            self.mouth_open = not self.mouth_open

        # If not moving, check for input and start moving
        if not self.moving:
            dx, dy = self.input_dir
            if dx != 0 or dy != 0:
                # Calculate next tile
                next_tx = self.tile_x + dx
                next_ty = self.tile_y + dy

                # Handle tunnel wrap
                if next_tx < 0:
                    next_tx = MAZE_WIDTH - 1
                elif next_tx >= MAZE_WIDTH:
                    next_tx = 0

                # Check if we can move there
                if self.is_walkable(maze, next_tx, next_ty):
                    self.target_x = next_tx
                    self.target_y = next_ty
                    self.face_dir = (dx, dy)
                    self.moving = True

        # If moving, interpolate toward target
        if self.moving:
            # Target pixel position
            target_px = self.target_x * TILE_SIZE + TILE_SIZE // 2
            target_py = self.target_y * TILE_SIZE + TILE_SIZE // 2

            # Handle tunnel wrap for pixel position
            if self.target_x == 0 and self.tile_x == MAZE_WIDTH - 1:
                target_px = GAME_WIDTH + TILE_SIZE // 2
            elif self.target_x == MAZE_WIDTH - 1 and self.tile_x == 0:
                target_px = -TILE_SIZE // 2

            # Move toward target
            diff_x = target_px - self.x
            diff_y = target_py - self.y

            if abs(diff_x) <= self.speed and abs(diff_y) <= self.speed:
                # Arrived at target tile
                self.tile_x = self.target_x
                self.tile_y = self.target_y
                self.x = self.tile_x * TILE_SIZE + TILE_SIZE // 2
                self.y = self.tile_y * TILE_SIZE + TILE_SIZE // 2
                self.moving = False

                # Wrap position for tunnel
                if self.x < 0:
                    self.x = GAME_WIDTH - TILE_SIZE // 2
                elif self.x >= GAME_WIDTH:
                    self.x = TILE_SIZE // 2
            else:
                # Keep moving
                if diff_x > 0:
                    self.x += self.speed
                elif diff_x < 0:
                    self.x -= self.speed
                if diff_y > 0:
                    self.y += self.speed
                elif diff_y < 0:
                    self.y -= self.speed

    def draw(self, surface):
        dx, dy = self.face_dir if self.face_dir != (0, 0) else self.input_dir

        if dx == 1:
            angle = 0
        elif dx == -1:
            angle = 180
        elif dy == -1:
            angle = 90
        elif dy == 1:
            angle = 270
        else:
            angle = 0

        mouth = 45 if self.mouth_open else 10
        radius = TILE_SIZE // 3

        size = radius * 2 + 4
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2

        points = [(c, c)]
        for i in range(int((360 - 2 * mouth) / 5) + 1):
            a = math.radians(mouth + i * 5)
            if a > math.radians(360 - mouth):
                break
            points.append((c + radius * math.cos(a), c - radius * math.sin(a)))
        points.append((c, c))

        if len(points) > 2:
            pygame.draw.polygon(surf, self.color, points)

        rotated = pygame.transform.rotate(surf, angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)

    def get_tile(self):
        """Get current tile position."""
        return (self.tile_x, self.tile_y)


class Ghost:
    def __init__(self, start_x, start_y, color, name, behavior, exit_delay):
        self.start_x = start_x
        self.start_y = start_y
        self.color = color
        self.name = name
        self.behavior = behavior
        self.exit_delay = exit_delay
        self.speed = 2
        self.reset()

    def reset(self):
        self.x = self.start_x * TILE_SIZE + TILE_SIZE // 2
        self.y = self.start_y * TILE_SIZE + TILE_SIZE // 2
        self.dir_x = 0
        self.dir_y = 0
        self.vulnerable = False
        self.vulnerable_timer = 0
        self.eaten = False
        self.in_house = True
        self.house_timer = 0
        self.last_tile = None

    def make_vulnerable(self, duration):
        if not self.eaten:
            self.vulnerable = True
            self.vulnerable_timer = duration

    def is_tile_walkable(self, maze, tile_x, tile_y, allow_door=False):
        """Check if a tile can be walked on by ghost."""
        # Handle tunnel
        if tile_x < 0 or tile_x >= MAZE_WIDTH:
            return True
        if tile_y < 0 or tile_y >= MAZE_HEIGHT:
            return False
        cell = maze[tile_y][tile_x]
        if cell == 1:  # Wall
            return False
        if cell == 4 and not allow_door:  # Ghost door
            return False
        return True

    def get_valid_directions(self, maze, tile_x, tile_y, allow_door=False):
        """Get list of valid movement directions from current tile."""
        directions = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            # Don't reverse direction (unless stuck)
            if (dx, dy) == (-self.dir_x, -self.dir_y) and (self.dir_x != 0 or self.dir_y != 0):
                continue

            next_x = tile_x + dx
            next_y = tile_y + dy

            # Handle tunnel wrap
            if next_x < 0:
                next_x = MAZE_WIDTH - 1
            elif next_x >= MAZE_WIDTH:
                next_x = 0

            if self.is_tile_walkable(maze, next_x, next_y, allow_door):
                directions.append((dx, dy))

        return directions

    def choose_direction(self, directions, target_x, target_y, tile_x, tile_y, flee=False):
        """Choose best direction toward or away from target."""
        if not directions:
            return (0, 0)

        if flee:
            # Move away from target
            return max(directions, key=lambda d:
                ((tile_x + d[0]) * TILE_SIZE - target_x)**2 +
                ((tile_y + d[1]) * TILE_SIZE - target_y)**2)
        else:
            # Move toward target
            return min(directions, key=lambda d:
                ((tile_x + d[0]) * TILE_SIZE - target_x)**2 +
                ((tile_y + d[1]) * TILE_SIZE - target_y)**2)

    def update(self, maze, pacman_x, pacman_y):
        # Update vulnerability timer
        if self.vulnerable:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.vulnerable = False

        # Handle ghost house
        if self.in_house:
            self.house_timer += 1
            if self.house_timer >= self.exit_delay:
                self.in_house = False
                # Exit to position above ghost house
                self.x = 13 * TILE_SIZE + TILE_SIZE // 2
                self.y = 11 * TILE_SIZE + TILE_SIZE // 2
                self.dir_x = -1
                self.dir_y = 0
                self.last_tile = (13, 11)
            return

        # Get current tile position
        tile_x = int(self.x // TILE_SIZE)
        tile_y = int(self.y // TILE_SIZE)
        center_x = tile_x * TILE_SIZE + TILE_SIZE // 2
        center_y = tile_y * TILE_SIZE + TILE_SIZE // 2

        # Get current speed
        speed = self.speed
        if self.vulnerable:
            speed = 1
        elif self.eaten:
            speed = 4

        # Check if at tile center
        at_center = abs(self.x - center_x) <= speed and abs(self.y - center_y) <= speed
        current_tile = (tile_x, tile_y)

        # Make decisions only at tile centers, and only once per tile
        if at_center and current_tile != self.last_tile:
            # Snap to center
            self.x = center_x
            self.y = center_y
            self.last_tile = current_tile

            if self.eaten:
                # Return to ghost house
                target_x = 13 * TILE_SIZE + TILE_SIZE // 2
                target_y = 14 * TILE_SIZE + TILE_SIZE // 2

                if tile_x == 13 and tile_y == 14:
                    self.eaten = False
                    self.in_house = True
                    self.house_timer = self.exit_delay // 2
                    self.x = self.start_x * TILE_SIZE + TILE_SIZE // 2
                    self.y = self.start_y * TILE_SIZE + TILE_SIZE // 2
                    self.dir_x = 0
                    self.dir_y = 0
                    self.last_tile = None
                    return

                directions = self.get_valid_directions(maze, tile_x, tile_y, allow_door=True)
                if not directions:
                    directions = [(-self.dir_x, -self.dir_y)]
                self.dir_x, self.dir_y = self.choose_direction(directions, target_x, target_y, tile_x, tile_y)

            else:
                # Normal ghost AI
                directions = self.get_valid_directions(maze, tile_x, tile_y)

                if not directions:
                    # Must reverse if stuck
                    directions = [(-self.dir_x, -self.dir_y)]

                if self.vulnerable:
                    # Run away from Pacman
                    self.dir_x, self.dir_y = self.choose_direction(directions, pacman_x, pacman_y, tile_x, tile_y, flee=True)
                elif self.behavior == 'chase':
                    # Chase Pacman directly
                    self.dir_x, self.dir_y = self.choose_direction(directions, pacman_x, pacman_y, tile_x, tile_y)
                elif self.behavior == 'random':
                    # Random movement
                    self.dir_x, self.dir_y = random.choice(directions)
                else:
                    # Mix of chase and random
                    if random.random() < 0.7:
                        self.dir_x, self.dir_y = self.choose_direction(directions, pacman_x, pacman_y, tile_x, tile_y)
                    else:
                        self.dir_x, self.dir_y = random.choice(directions)

        # Move only if we have a valid direction
        if self.dir_x != 0 or self.dir_y != 0:
            self.x += self.dir_x * speed
            self.y += self.dir_y * speed

        # Tunnel wrapping
        if self.x < 0:
            self.x = GAME_WIDTH - TILE_SIZE // 2
            self.last_tile = None
        elif self.x >= GAME_WIDTH:
            self.x = TILE_SIZE // 2
            self.last_tile = None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)

        if self.eaten:
            pygame.draw.circle(surface, WHITE, (x - 3, y), 3)
            pygame.draw.circle(surface, WHITE, (x + 3, y), 3)
            pygame.draw.circle(surface, BLACK, (x - 2, y), 1)
            pygame.draw.circle(surface, BLACK, (x + 4, y), 1)
            return

        if self.vulnerable:
            color = GHOST_FLASH if (self.vulnerable_timer < 120 and (self.vulnerable_timer // 15) % 2 == 0) else GHOST_VULNERABLE
        else:
            color = self.color

        size = TILE_SIZE // 3
        pygame.draw.circle(surface, color, (x, y - 2), size)
        pygame.draw.rect(surface, color, (x - size, y - 2, size * 2, size))
        for i in range(3):
            wx = x - size + i * (size * 2 // 3) + size // 3
            pygame.draw.circle(surface, color, (wx, y + size - 3), size // 3 + 1)

        pygame.draw.circle(surface, WHITE, (x - 3, y - 3), 3)
        pygame.draw.circle(surface, WHITE, (x + 3, y - 3), 3)
        if not self.vulnerable:
            pygame.draw.circle(surface, BLUE, (x - 3 + self.dir_x, y - 3 + self.dir_y), 1)
            pygame.draw.circle(surface, BLUE, (x + 3 + self.dir_x, y - 3 + self.dir_y), 1)


class Game:
    def __init__(self):
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.fullscreen = False
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.high_score_manager = HighScoreManager()

        self.state = 'menu'
        self.pacman_color_name = 'yellow'
        self.pacman_color = PACMAN_COLORS['yellow']
        self.color_options = list(PACMAN_COLORS.keys())
        self.selected_color_index = 0
        self.player_name = ""

        self.reset_game()

    def reset_game(self):
        self.maze = []
        self.pellets = set()
        self.power_pellets = set()

        for y, row in enumerate(MAZE_LAYOUT):
            maze_row = []
            for x, char in enumerate(row):
                maze_row.append(int(char))
                if char == '2':
                    self.pellets.add((x, y))
                elif char == '3':
                    self.power_pellets.add((x, y))
            self.maze.append(maze_row)

        # Start Pacman at a good position
        self.pacman = Pacman(1, 1, self.pacman_color)

        self.ghosts = [
            Ghost(12, 14, GHOST_COLORS['blinky'], 'blinky', 'chase', 1),
            Ghost(13, 14, GHOST_COLORS['pinky'], 'pinky', 'ambush', 60),
            Ghost(14, 14, GHOST_COLORS['inky'], 'inky', 'random', 120),
            Ghost(15, 14, GHOST_COLORS['clyde'], 'clyde', 'random', 180),
        ]

        self.score = 0
        self.lives = 3
        self.ghost_eat_streak = 0

    def reset_positions(self):
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()

    def reload_pellets(self):
        self.pellets = set()
        self.power_pellets = set()
        for y, row in enumerate(MAZE_LAYOUT):
            for x, char in enumerate(row):
                if char == '2':
                    self.pellets.add((x, y))
                elif char == '3':
                    self.power_pellets.add((x, y))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.RESIZABLE)

    def scale_display(self):
        sw, sh = self.screen.get_size()
        scale = min(sw / GAME_WIDTH, sh / GAME_HEIGHT)
        new_w, new_h = int(GAME_WIDTH * scale), int(GAME_HEIGHT * scale)
        scaled = pygame.transform.scale(self.game_surface, (new_w, new_h))
        self.screen.fill(BLACK)
        self.screen.blit(scaled, ((sw - new_w) // 2, (sh - new_h) // 2))

    def draw_maze(self):
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 1:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.game_surface, WALL_BLUE, rect)
                    pygame.draw.rect(self.game_surface, BLACK, rect.inflate(-4, -4))

        for x, y in self.pellets:
            pygame.draw.circle(self.game_surface, PELLET_COLOR,
                (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), 3)

        pulse = abs((pygame.time.get_ticks() // 100) % 10 - 5)
        for x, y in self.power_pellets:
            pygame.draw.circle(self.game_surface, POWER_PELLET_COLOR,
                (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), 6 + pulse)

    def draw_hud(self):
        self.game_surface.blit(self.font.render(f"Score: {self.score}", True, WHITE), (10, GAME_HEIGHT - 50))
        self.game_surface.blit(self.font.render(f"Lives: {self.lives}", True, WHITE), (GAME_WIDTH - 120, GAME_HEIGHT - 50))
        self.game_surface.blit(self.small_font.render("Arrow Keys/WASD to move, F11 fullscreen", True, (100, 100, 100)), (GAME_WIDTH // 2 - 140, GAME_HEIGHT - 20))

    def draw_menu(self):
        self.game_surface.fill(BLACK)
        title = self.font.render("PACMAN", True, PACMAN_COLORS['yellow'])
        self.game_surface.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 100)))

        for text, y in [("ENTER - Start", 200), ("C - Change Color", 250), ("H - High Scores", 300), ("F11 - Fullscreen", 350), ("Q - Quit", 400)]:
            r = self.small_font.render(text, True, WHITE)
            self.game_surface.blit(r, r.get_rect(center=(GAME_WIDTH // 2, y)))

        r = self.small_font.render(f"Color: {self.pacman_color_name.upper()}", True, self.pacman_color)
        self.game_surface.blit(r, r.get_rect(center=(GAME_WIDTH // 2, 480)))
        pygame.draw.circle(self.game_surface, self.pacman_color, (GAME_WIDTH // 2, 540), 30)
        pygame.draw.polygon(self.game_surface, BLACK, [(GAME_WIDTH // 2, 540), (GAME_WIDTH // 2 + 35, 525), (GAME_WIDTH // 2 + 35, 555)])

    def draw_color_select(self):
        self.game_surface.fill(BLACK)
        self.game_surface.blit(self.font.render("SELECT COLOR", True, WHITE),
            self.font.render("SELECT COLOR", True, WHITE).get_rect(center=(GAME_WIDTH // 2, 80)))

        for i, name in enumerate(self.color_options):
            y = 150 + i * 80
            if i == self.selected_color_index:
                pygame.draw.rect(self.game_surface, WHITE, (GAME_WIDTH // 2 - 150, y - 25, 300, 60), 2)
            pygame.draw.circle(self.game_surface, PACMAN_COLORS[name], (GAME_WIDTH // 2 - 80, y), 20)
            self.game_surface.blit(self.font.render(name.upper(), True, PACMAN_COLORS[name]), (GAME_WIDTH // 2 - 40, y - 15))

        for i, t in enumerate(["UP/DOWN select", "ENTER confirm", "ESC back"]):
            self.game_surface.blit(self.small_font.render(t, True, WHITE), (GAME_WIDTH // 2 - 60, 560 + i * 25))

    def draw_game_over(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        self.game_surface.blit(overlay, (0, 0))

        self.game_surface.blit(self.font.render("GAME OVER", True, (255, 0, 0)),
            self.font.render("GAME OVER", True, (255, 0, 0)).get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50)))
        self.game_surface.blit(self.font.render(f"Score: {self.score}", True, WHITE),
            self.font.render(f"Score: {self.score}", True, WHITE).get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2)))

        msg = "NEW HIGH SCORE! ENTER to save" if self.high_score_manager.is_high_score(self.score) else "ENTER menu, R retry"
        self.game_surface.blit(self.small_font.render(msg, True, WHITE),
            self.small_font.render(msg, True, WHITE).get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 50)))

    def draw_high_score_entry(self):
        self.game_surface.fill(BLACK)
        self.game_surface.blit(self.font.render("NEW HIGH SCORE!", True, PACMAN_COLORS['yellow']),
            self.font.render("NEW HIGH SCORE!", True, PACMAN_COLORS['yellow']).get_rect(center=(GAME_WIDTH // 2, 100)))
        self.game_surface.blit(self.font.render(f"Score: {self.score}", True, WHITE),
            self.font.render(f"Score: {self.score}", True, WHITE).get_rect(center=(GAME_WIDTH // 2, 160)))
        self.game_surface.blit(self.small_font.render("Enter name:", True, WHITE),
            self.small_font.render("Enter name:", True, WHITE).get_rect(center=(GAME_WIDTH // 2, 250)))
        pygame.draw.rect(self.game_surface, WHITE, (GAME_WIDTH // 2 - 100, 280, 200, 40), 2)
        self.game_surface.blit(self.font.render(self.player_name + "_", True, WHITE),
            self.font.render(self.player_name + "_", True, WHITE).get_rect(center=(GAME_WIDTH // 2, 300)))

    def draw_high_scores(self):
        self.game_surface.fill(BLACK)
        self.game_surface.blit(self.font.render("HIGH SCORES", True, PACMAN_COLORS['yellow']),
            self.font.render("HIGH SCORES", True, PACMAN_COLORS['yellow']).get_rect(center=(GAME_WIDTH // 2, 60)))

        scores = self.high_score_manager.get_scores()
        if not scores:
            self.game_surface.blit(self.small_font.render("No scores yet!", True, WHITE),
                self.small_font.render("No scores yet!", True, WHITE).get_rect(center=(GAME_WIDTH // 2, 200)))
        else:
            for i, e in enumerate(scores):
                y = 120 + i * 40
                self.game_surface.blit(self.small_font.render(f"{i+1}. {e['name'][:10]}", True, WHITE), (GAME_WIDTH // 2 - 100, y))
                self.game_surface.blit(self.small_font.render(str(e['score']), True, WHITE), (GAME_WIDTH // 2 + 50, y))

        self.game_surface.blit(self.small_font.render("ESC to go back", True, WHITE),
            self.small_font.render("ESC to go back", True, WHITE).get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 60)))

    def run(self):
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

                    elif self.state == 'menu':
                        if event.key == pygame.K_RETURN:
                            self.reset_game()
                            self.state = 'playing'
                        elif event.key == pygame.K_c:
                            self.state = 'color_select'
                        elif event.key == pygame.K_h:
                            self.state = 'high_scores'
                        elif event.key == pygame.K_q:
                            running = False

                    elif self.state == 'color_select':
                        if event.key == pygame.K_UP:
                            self.selected_color_index = (self.selected_color_index - 1) % len(self.color_options)
                        elif event.key == pygame.K_DOWN:
                            self.selected_color_index = (self.selected_color_index + 1) % len(self.color_options)
                        elif event.key == pygame.K_RETURN:
                            self.pacman_color_name = self.color_options[self.selected_color_index]
                            self.pacman_color = PACMAN_COLORS[self.pacman_color_name]
                            self.state = 'menu'
                        elif event.key == pygame.K_ESCAPE:
                            self.state = 'menu'

                    elif self.state == 'playing':
                        if event.key == pygame.K_ESCAPE:
                            self.state = 'menu'

                    elif self.state == 'game_over':
                        if event.key == pygame.K_RETURN:
                            if self.high_score_manager.is_high_score(self.score):
                                self.player_name = ""
                                self.state = 'high_score_entry'
                            else:
                                self.state = 'menu'
                        elif event.key == pygame.K_r:
                            self.reset_game()
                            self.state = 'playing'

                    elif self.state == 'high_score_entry':
                        if event.key == pygame.K_RETURN and self.player_name:
                            self.high_score_manager.add_score(self.player_name, self.score)
                            self.state = 'high_scores'
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif len(self.player_name) < 10 and (event.unicode.isalnum() or event.unicode == ' '):
                            self.player_name += event.unicode

                    elif self.state == 'high_scores':
                        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                            self.state = 'menu'

                if event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Game logic
            if self.state == 'playing':
                # Read keyboard for movement
                keys = pygame.key.get_pressed()

                # RIGHT
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.pacman.request_direction(1, 0)
                # LEFT
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.pacman.request_direction(-1, 0)
                # UP
                elif keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.pacman.request_direction(0, -1)
                # DOWN
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.pacman.request_direction(0, 1)

                # Update Pacman
                self.pacman.update(self.maze)

                # Check pellet collection
                tile = self.pacman.get_tile()
                if tile in self.pellets:
                    self.pellets.remove(tile)
                    self.score += 10
                if tile in self.power_pellets:
                    self.power_pellets.remove(tile)
                    self.score += 50
                    self.ghost_eat_streak = 0
                    for g in self.ghosts:
                        g.make_vulnerable(360)

                # Update ghosts
                for g in self.ghosts:
                    g.update(self.maze, self.pacman.x, self.pacman.y)

                # Check ghost collision
                for g in self.ghosts:
                    if g.eaten or g.in_house:
                        continue
                    dist = math.sqrt((self.pacman.x - g.x)**2 + (self.pacman.y - g.y)**2)
                    if dist < TILE_SIZE * 0.6:
                        if g.vulnerable:
                            g.eaten = True
                            self.ghost_eat_streak += 1
                            self.score += 200 * (2 ** (self.ghost_eat_streak - 1))
                        else:
                            self.lives -= 1
                            if self.lives <= 0:
                                self.state = 'game_over'
                            else:
                                self.reset_positions()
                            break

                # Level complete
                if not self.pellets and not self.power_pellets:
                    self.reload_pellets()
                    self.reset_positions()

            # Draw
            self.game_surface.fill(BLACK)

            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'color_select':
                self.draw_color_select()
            elif self.state == 'playing':
                self.draw_maze()
                self.pacman.draw(self.game_surface)
                for g in self.ghosts:
                    g.draw(self.game_surface)
                self.draw_hud()
            elif self.state == 'game_over':
                self.draw_maze()
                self.pacman.draw(self.game_surface)
                for g in self.ghosts:
                    g.draw(self.game_surface)
                self.draw_hud()
                self.draw_game_over()
            elif self.state == 'high_score_entry':
                self.draw_high_score_entry()
            elif self.state == 'high_scores':
                self.draw_high_scores()

            self.scale_display()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
