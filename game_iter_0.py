import time
import pygame
from coin import Coin


class PygameInputController:
    def __init__(self):
        pass

    def get_pressed_keys(self):
        keys = pygame.key.get_pressed()
        pressed = set()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            pressed.add("a")
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            pressed.add("d")
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            pressed.add("w")
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            pressed.add("s")
        if keys[pygame.K_q]:
            pressed.add("q")
        if keys[pygame.K_r]:
            pressed.add("r")

        return pressed


class GameField:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def clamp(self, x, y):
        return (max(self.x_min, min(self.x_max, x)), max(self.y_min, min(self.y_max, y)),
                self.x_min > x or self.x_max < x, self.y_min > y or self.y_max < y)


class Player:
    def __init__(self, x, y, speed_x=3, speed_y=3, radius=12):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius

    def move(self, left, right, up, down, game_field):
        self.x += self.speed_x * right - self.speed_x * left
        self.y += self.speed_y * down - self.speed_y * up
        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y

    def check_collision(self, other_x, other_y, other_radius):
        dx = self.x - other_x
        dy = self.y - other_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance < (self.radius + other_radius)


class NPC:
    def __init__(self, x, y, speed_x=0, speed_y=2, radius=12):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y
        self.x, self.y, x_edge, y_edge = game_field.clamp(self.x, self.y)

        if x_edge:
            self.speed_x = -self.speed_x
        if y_edge:
            self.speed_y = -self.speed_y


# === Level Configuration ===
class Level:
    def __init__(self, start_zone, end_zone, npcs, coins, player_start):
        self.start_zone = start_zone  # (x, y, width, height)
        self.end_zone = end_zone      # (x, y, width, height)
        self.npcs = npcs
        self.coins = coins
        self.player_start = player_start


def create_level_1():
    start_zone = (0, 150, 80, 200)      # left
    end_zone = (420, 150, 80, 200)      # right
    player_start = (40, 250)

    # create 5 NPCs move up-down
    npcs = [
        NPC(150, 180, speed_x=0, speed_y=3),
        NPC(200, 320, speed_x=0, speed_y=-3),
        NPC(250, 200, speed_x=0, speed_y=4),
        NPC(300, 300, speed_x=0, speed_y=-4),
        NPC(350, 250, speed_x=0, speed_y=3),
    ]

    # create 3 Coins
    coins = [
        Coin(180, 250),
        Coin(270, 250),
        Coin(360, 250),
    ]

    return Level(start_zone, end_zone, npcs, coins, player_start)

def create_level_2():
    pass


class GameEngine:
    def __init__(self, graph_engine, input_controller, game_field, level, *, fps=60):
        self.graph_engine = graph_engine
        self.game_field = game_field
        self.level = level
        self.fps = fps
        self.input_controller = input_controller

        # Player
        px, py = level.player_start
        self.player = Player(px, py)

        # NPCs and Coins from level
        self.npcs = level.npcs
        self.coins = level.coins

        # Game state
        self.points = 0
        self.deaths = 0
        self.level_complete = False

    def check_in_zone(self, x, y, zone):
        """check if the player is in the zone"""
        zx, zy, zw, zh = zone
        return zx <= x <= zx + zw and zy <= y <= zy + zh

    def update_state(self, pressed_keys):
        # Move NPCs
        for npc in self.npcs:
            npc.move(self.game_field)

        # Move Player
        self.player.move(
            "a" in pressed_keys,
            "d" in pressed_keys,
            "w" in pressed_keys,
            "s" in pressed_keys,
            self.game_field
        )

        # Check collision with NPCs (if not in the safe zone)
        in_start = self.check_in_zone(self.player.x, self.player.y, self.level.start_zone)
        in_end = self.check_in_zone(self.player.x, self.player.y, self.level.end_zone)

        if not in_start and not in_end:
            for npc in self.npcs:
                if self.player.check_collision(npc.x, npc.y, npc.radius):
                    self.player.reset()
                    self.deaths += 1
                    # Reset coins when die
                    for coin in self.coins:
                        coin.collected = False
                    self.points = 0
                    break

        # Check collision with Coins
        for coin in self.coins:
            if not coin.collected and coin.check_collision(self.player.x, self.player.y, self.player.radius):
                coin.collected = True
                self.points += 1

        # Check win condition
        total_coins = len(self.coins)
        if in_end and self.points >= total_coins:
            self.level_complete = True

        # Quit
        if "q" in pressed_keys:
            self.running = False

        # Restart
        if "r" in pressed_keys:
            self.restart_level()

    def restart_level(self):
        self.player.reset()
        self.points = 0
        for coin in self.coins:
            coin.collected = False

    def render_state(self):
        self.graph_engine.start_frame()

        # Render zones
        self.graph_engine.render_zone(self.level.start_zone, "green")
        self.graph_engine.render_zone(self.level.end_zone, "green")

        # Render play area
        self.graph_engine.render_play_area(self.game_field)

        # Render Coins
        for coin in self.coins:
            if not coin.collected:
                self.graph_engine.render_circle(coin.x, coin.y, coin.radius, "yellow")

        # Render NPCs
        for npc in self.npcs:
            self.graph_engine.render_circle(npc.x, npc.y, npc.radius, "blue")

        # Render Player
        self.graph_engine.render_circle(self.player.x, self.player.y, self.player.radius, "red")

        # Render UI
        total_coins = len(self.coins)
        self.graph_engine.render_ui(self.points, total_coins, self.deaths, self.level_complete)

        self.graph_engine.show_frame()

    def run_game(self):
        self.running = True
        while self.running:
            self.render_state()
            pressed_keys = self.input_controller.get_pressed_keys()
            self.update_state(pressed_keys)
            time.sleep(1 / self.fps)


class GraphicsEngine:
    def __init__(self, width=500, height=500):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("The World's Hardest Game - Level 1")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)

    def start_frame(self):
        self.screen.fill((255, 255, 255))  # white background
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def show_frame(self):
        pygame.display.flip()

    def render_zone(self, zone, color):
        colors = {"green": (144, 238, 144), "red": (255, 100, 100)}
        x, y, w, h = zone
        pygame.draw.rect(self.screen, colors.get(color, (200, 200, 200)), (x, y, w, h))

    def render_play_area(self, game_field):
        # player area
        rect = (game_field.x_min, game_field.y_min,
                game_field.x_max - game_field.x_min,
                game_field.y_max - game_field.y_min)
        pygame.draw.rect(self.screen, (230, 230, 230), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def render_circle(self, x, y, radius, color):
        colors = {
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 215, 0),
        }
        pygame.draw.circle(self.screen, colors.get(color, (200, 200, 200)), (int(x), int(y)), radius)
        # Draw Stroke
        pygame.draw.circle(self.screen, (0, 0, 0), (int(x), int(y)), radius, 1)

    def render_ui(self, points, total, deaths, level_complete):
        # Show Points
        text = self.font.render(f"Coins: {points}/{total}  Deaths: {deaths}", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

        # Show text after compleate
        if level_complete:
            win_text = self.font.render("LEVEL COMPLETE! Press R to restart", True, (0, 128, 0))
            self.screen.blit(win_text, (80, 460))
        elif points < total:
            hint = self.font.render("Collect all coins to finish!", True, (100, 100, 100))
            self.screen.blit(hint, (120, 460))


if __name__ == "__main__":
    # create level 1
    level = create_level_1()

    # Game field
    game_field = GameField(0, 150, 500, 350)

    graphics = GraphicsEngine(500, 500)
    input_controller = PygameInputController()

    game_engine = GameEngine(
        graphics,
        input_controller,
        game_field,
        level,
        fps=60
    )

    game_engine.run_game()