import time

from kb_poller import KBPoller


class InputController:
    def __init__(self, kb_poller: KBPoller):
        self.kb_poller = kb_poller

    def get_pressed_keys(self):
        return self.kb_poller.pressed


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
    def __init__(self, x, y, speed_x=1, speed_y=1):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, left, right, up, down, game_field):
        self.x += self.speed_x * right - self.speed_x * left
        self.y += self.speed_y * down - self.speed_y * up

        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)


class NPC:
    def __init__(self, x, y, speed_x=1, speed_y=1):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y

        self.x, self.y, x_edge, y_edge = game_field.clamp(self.x, self.y)

        if x_edge:
            self.speed_x = -self.speed_x

        if y_edge:
            self.speed_y = -self.speed_y


class GameEngine:
    def __init__(self, graph_engine, input_controller, game_field, player, npc, *, fps=60):

        self.graph_engine = graph_engine

        self.game_field = game_field
        self.player = player
        self.npc = npc
        self.fps = fps

        self.input_controller = input_controller

    def update_state(self, pressed_keys):
        self.npc.move(self.game_field)
        self.player.move("a" in pressed_keys, "d" in pressed_keys, "w" in pressed_keys, "s" in pressed_keys, self.game_field)

        if "q" in pressed_keys:
            self.running = False

    def render_state(self):
        self.graph_engine.start_frame()

        self.graph_engine.render_circle(self.player.x, self.player.y, 20, "red")
        self.graph_engine.render_circle(self.npc.x, self.npc.y, 20, "blue")

        self.graph_engine.show_frame()

    def run_game(self):
        self.running = True
        while self.running:
            self.render_state()

            pressed_keys = self.input_controller.get_pressed_keys()
            self.update_state(pressed_keys)

            time.sleep(1 / self.fps)


class GraphicsEngine:
    def __init__(self):
        pass

    def start_frame(self):
        pass

    def show_frame(self):
        pass

    def render_circle(self, x, y, radius, color):
        print(f"{color} circle is at:", x, y)


if __name__ == "__main__":
    game_field = GameField(0, 0, 100, 100)
    player = Player(50, 50)
    npc = NPC(70, 70, 2, 1)

    game_engine = GameEngine(GraphicsEngine(), InputController(KBPoller()), game_field, player, npc, fps=15)
    game_engine.run_game()