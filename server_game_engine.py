import time
import random
from bullet import Bullet
from coin import Coin
from game_field import GameField


class NetPlayer:
    """Player class for networked multiplayer game."""
    def __init__(self, player_id, x, y, speed_x=3, speed_y=3, radius=12):
        self.id = player_id
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius
        self.direction = "right"
        # stats
        self.coins = 0
        self.deaths = 0
        self.kills = 0
        # fire cooldown (frames)
        self.fire_cooldown = 0

    def move(self, left, right, up, down, game_field):
        if up:
            self.direction = "up"
        if down:
            self.direction = "down"
        if left:
            self.direction = "left"
        if right:
            self.direction = "right"

        self.x += self.speed_x * right - self.speed_x * left
        self.y += self.speed_y * down - self.speed_y * up
        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = "right"

    def check_collision(self, other_x, other_y, other_radius):
        dx = self.x - other_x
        dy = self.y - other_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance < (self.radius + other_radius)

    def fire(self):
        return Bullet(self.x, self.y, self.direction)


class NetNPC:
    """NPC class for networked multiplayer game."""
    def __init__(self, x, y, speed_x=0, speed_y=2, radius=12):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius
        self.active = True

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y
        self.x, self.y, x_edge, y_edge = game_field.clamp(self.x, self.y)
        if x_edge:
            self.speed_x = -self.speed_x
        if y_edge:
            self.speed_y = -self.speed_y


class NPCSpawner:
    def __init__(self, game_field, spawn_interval=120, max_npcs=15):
        self.game_field = game_field
        self.spawn_interval = spawn_interval
        self.max_npcs = max_npcs
        self.frame_counter = 0

    def update(self, npcs):
        self.frame_counter += 1
        if self.frame_counter >= self.spawn_interval and len(npcs) < self.max_npcs:
            self.frame_counter = 0
            x = random.randint(int(self.game_field.x_min + 100),
                               int(self.game_field.x_max - 100))
            y = random.randint(int(self.game_field.y_min + 30),
                               int(self.game_field.y_max - 30))
            if random.choice([True, False]):
                sx, sy = 0, random.choice([-3, -2, 2, 3])
            else:
                sx, sy = random.choice([-3, -2, 2, 3]), 0
            npcs.append(NetNPC(x, y, sx, sy))


class ServerGameEngine:
    """Server-side game engine for multiplayer. No graphics - headless."""

    FIRE_COOLDOWN_FRAMES = 15  # ~0.25s at 60fps

    def __init__(self, game_field, start_zone, end_zone, *, fps=60):
        self.game_field = game_field
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.fps = fps

        # players dict: player_id -> NetPlayer
        self.players = {}
        self.actions_for_players = {}

        # NPCs
        self.npcs = [
            NetNPC(150, 180, speed_x=0, speed_y=3),
            NetNPC(200, 320, speed_x=0, speed_y=-3),
            NetNPC(250, 200, speed_x=0, speed_y=4),
            NetNPC(300, 300, speed_x=0, speed_y=-4),
            NetNPC(350, 250, speed_x=0, speed_y=3),
        ]

        # Coins (shared, first-come-first-served)
        self.coins = [
            Coin(180, 250),
            Coin(270, 250),
            Coin(360, 250),
        ]

        # Bullets (each tracks owner)
        self.bullets = []

        # NPC Spawner
        self.spawner = NPCSpawner(game_field, spawn_interval=fps * 2, max_npcs=15)

    # --- Player management (called from network threads) ---

    def add_player(self, player_id):
        # Stagger spawn positions
        spawn_y = 200 + (player_id * 30) % 100
        player = NetPlayer(player_id, 40, spawn_y)
        self.players[player_id] = player
        print(f"[Engine] Player {player_id} added at (40, {spawn_y})")

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            if player_id in self.actions_for_players:
                del self.actions_for_players[player_id]
            print(f"[Engine] Player {player_id} removed")

    def set_player_actions(self, player_id, actions):
        self.actions_for_players[player_id] = actions

    # --- Game state serialization ---

    def get_game_state_data(self):
        players_data = {}
        for pid, p in self.players.items():
            players_data[str(pid)] = [p.x, p.y, p.direction, p.coins, p.deaths, p.kills]

        npcs_data = [[n.x, n.y, n.radius] for n in self.npcs]

        coins_data = []
        for c in self.coins:
            collected_by = getattr(c, "collected_by", None)
            coins_data.append([c.x, c.y, c.radius, collected_by])

        bullets_data = [[b.x, b.y, b.radius] for b in self.bullets]

        return {
            "players": players_data,
            "npcs": npcs_data,
            "coins": coins_data,
            "bullets": bullets_data,
            "field": [self.game_field.x_min, self.game_field.y_min,
                      self.game_field.x_max, self.game_field.y_max],
            "start_zone": list(self.start_zone),
            "end_zone": list(self.end_zone),
        }

    # --- Game logic ---

    def _check_in_zone(self, x, y, zone):
        zx, zy, zw, zh = zone
        return zx <= x <= zx + zw and zy <= y <= zy + zh

    def update_state(self):
        # Spawn NPCs
        self.spawner.update(self.npcs)

        # Move NPCs
        for npc in self.npcs:
            npc.move(self.game_field)

        # Process each player
        for pid, player in list(self.players.items()):
            actions = self.actions_for_players.get(pid, {})

            # Move
            player.move(
                "left" in actions,
                "right" in actions,
                "up" in actions,
                "down" in actions,
                self.game_field
            )

            # Fire
            if player.fire_cooldown > 0:
                player.fire_cooldown -= 1

            if "fire" in actions and player.fire_cooldown == 0:
                bullet = player.fire()
                bullet.owner_id = pid
                self.bullets.append(bullet)
                player.fire_cooldown = self.FIRE_COOLDOWN_FRAMES

        # Move Bullets
        for bullet in self.bullets:
            bullet.move()

        # Bullet vs NPC collision
        for bullet in self.bullets:
            if not bullet.active:
                continue
            for npc in self.npcs:
                if not npc.active:
                    continue
                if bullet.check_collision(npc.x, npc.y, npc.radius):
                    bullet.active = False
                    npc.active = False
                    # Credit kill to bullet owner
                    owner_id = getattr(bullet, "owner_id", None)
                    if owner_id and owner_id in self.players:
                        self.players[owner_id].kills += 1

        # Remove inactive NPCs and bullets
        self.npcs = [n for n in self.npcs if n.active]
        self.bullets = [b for b in self.bullets
                        if b.active and not b.is_out_of_bounds(self.game_field)]

        # Player vs NPC collision (death)
        for pid, player in list(self.players.items()):
            in_start = self._check_in_zone(player.x, player.y, self.start_zone)
            in_end = self._check_in_zone(player.x, player.y, self.end_zone)

            if not in_start and not in_end:
                for npc in self.npcs:
                    if player.check_collision(npc.x, npc.y, npc.radius):
                        player.reset()
                        player.deaths += 1
                        # Reset coins this player collected
                        for coin in self.coins:
                            if getattr(coin, "collected_by", None) == pid:
                                coin.collected = False
                                coin.collected_by = None
                        player.coins = 0
                        break

        # Coin collection (first-come-first-served)
        for coin in self.coins:
            if coin.collected:
                continue
            for pid, player in self.players.items():
                if coin.check_collision(player.x, player.y, player.radius):
                    coin.collected = True
                    coin.collected_by = pid
                    player.coins += 1
                    break

    def run_game(self):
        """Main game loop - runs in main thread."""
        self.running = True
        print(f"[Engine] Game loop started at {self.fps} FPS")
        while self.running:
            self.update_state()
            time.sleep(1 / self.fps)
