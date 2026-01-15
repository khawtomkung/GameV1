import time

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