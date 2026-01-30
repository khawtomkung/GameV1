import json
import socket
import pygame

# --- Network config ---
HOST = "127.0.0.1"
PORT = 21001

# --- Colors ---
PLAYER_COLORS = {
    0: (255, 0, 0),       # red (fallback)
    1: (255, 0, 0),       # red
    2: (0, 200, 0),       # green
    3: (255, 165, 0),     # orange
    4: (200, 0, 200),     # purple
    5: (0, 200, 200),     # cyan
    6: (255, 105, 180),   # pink
}
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 215, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_ZONE = (144, 238, 144)
COLOR_FIELD = (230, 230, 230)
COLOR_BG = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)
COLOR_COIN_TAKEN = (180, 180, 120)

WINDOW_W = 500
WINDOW_H = 500


def get_player_color(player_id, my_id):
    """Return a distinct color for each player."""
    if player_id == my_id:
        return (255, 0, 0)  # always red for self
    return PLAYER_COLORS.get(player_id, (0, 100, 255))


def render_state(screen, font, state, my_id):
    """Render full game state received from server."""
    screen.fill(COLOR_BG)

    # --- Draw zones ---
    if "start_zone" in state:
        sz = state["start_zone"]
        pygame.draw.rect(screen, COLOR_ZONE, sz)
    if "end_zone" in state:
        ez = state["end_zone"]
        pygame.draw.rect(screen, COLOR_ZONE, ez)

    # --- Draw play area border ---
    if "field" in state:
        f = state["field"]
        rect = (f[0], f[1], f[2] - f[0], f[3] - f[1])
        pygame.draw.rect(screen, COLOR_FIELD, rect)
        pygame.draw.rect(screen, COLOR_BLACK, rect, 2)

    # --- Draw coins ---
    for coin_data in state.get("coins", []):
        cx, cy, cr, collected_by = coin_data
        if collected_by is None:
            pygame.draw.circle(screen, COLOR_YELLOW, (int(cx), int(cy)), cr)
            pygame.draw.circle(screen, COLOR_BLACK, (int(cx), int(cy)), cr, 2)
        else:
            # collected coin - dim
            pygame.draw.circle(screen, COLOR_COIN_TAKEN, (int(cx), int(cy)), cr)
            pygame.draw.circle(screen, COLOR_GRAY, (int(cx), int(cy)), cr, 1)

    # --- Draw bullets ---
    for bdata in state.get("bullets", []):
        bx, by, br = bdata
        pygame.draw.circle(screen, COLOR_WHITE, (int(bx), int(by)), br)
        pygame.draw.circle(screen, COLOR_BLACK, (int(bx), int(by)), br, 1)

    # --- Draw NPCs ---
    for ndata in state.get("npcs", []):
        nx, ny, nr = ndata
        pygame.draw.circle(screen, COLOR_BLUE, (int(nx), int(ny)), nr)
        pygame.draw.circle(screen, COLOR_BLACK, (int(nx), int(ny)), nr, 2)

    # --- Draw players ---
    players = state.get("players", {})
    for pid_str, pdata in players.items():
        pid = int(pid_str)
        px, py, direction, coins, deaths, kills = pdata
        color = get_player_color(pid, my_id)

        # body circle
        radius = 12
        pygame.draw.circle(screen, color, (int(px), int(py)), radius)
        pygame.draw.circle(screen, COLOR_BLACK, (int(px), int(py)), radius, 2)

        # direction triangle
        tri_size = 8
        x, y, r = int(px), int(py), radius
        if direction == "up":
            points = [(x, y - r - 5), (x - tri_size, y - r + 5), (x + tri_size, y - r + 5)]
        elif direction == "down":
            points = [(x, y + r + 5), (x - tri_size, y + r - 5), (x + tri_size, y + r - 5)]
        elif direction == "left":
            points = [(x - r - 5, y), (x - r + 5, y - tri_size), (x - r + 5, y + tri_size)]
        else:
            points = [(x + r + 5, y), (x + r - 5, y - tri_size), (x + r - 5, y + tri_size)]
        pygame.draw.polygon(screen, COLOR_WHITE, points)
        pygame.draw.polygon(screen, COLOR_BLACK, points, 2)

        # label
        label = "YOU" if pid == my_id else f"P{pid}"
        label_surf = font.render(label, True, COLOR_BLACK)
        screen.blit(label_surf, (int(px) - label_surf.get_width() // 2, int(py) - 25))

    # --- HUD / Scoreboard ---
    y_offset = 10
    header = font.render("SCOREBOARD", True, COLOR_BLACK)
    screen.blit(header, (10, y_offset))
    y_offset += 22

    for pid_str, pdata in players.items():
        pid = int(pid_str)
        _, _, _, coins, deaths, kills = pdata
        tag = "YOU" if pid == my_id else f"P{pid}"
        color = get_player_color(pid, my_id)
        line = f"{tag}: Coins={coins} Kills={kills} Deaths={deaths}"
        line_surf = font.render(line, True, color)
        screen.blit(line_surf, (10, y_offset))
        y_offset += 18

    # --- Controls hint ---
    controls = font.render("WASD:Move  SPACE:Fire  Q:Quit", True, COLOR_GRAY)
    screen.blit(controls, (80, WINDOW_H - 25))

    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Network Game - Client")
    font = pygame.font.Font(None, 22)
    clock = pygame.time.Clock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        my_id = None
        running = True

        while running:
            # --- Handle pygame events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not running:
                break

            # --- Capture input ---
            keys = pygame.key.get_pressed()
            actions = {}
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                actions["left"] = 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                actions["right"] = 1
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                actions["up"] = 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                actions["down"] = 1
            if keys[pygame.K_SPACE]:
                actions["fire"] = 1
            if keys[pygame.K_q]:
                running = False
                break

            # --- Send actions to server ---
            try:
                s.sendall(json.dumps(actions).encode())
            except Exception as e:
                print(f"Send error: {e}")
                break

            # --- Receive game state ---
            try:
                data = s.recv(8192)
                if not data:
                    print("Server disconnected")
                    break
                state = json.loads(data.decode())
            except Exception as e:
                print(f"Receive error: {e}")
                break

            # Identify self
            if my_id is None:
                my_id = state.get("self")

            # --- Render ---
            render_state(screen, font, state, my_id)
            clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
