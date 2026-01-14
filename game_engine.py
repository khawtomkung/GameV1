import time

class GameEngine:
    def __init__(self, player, npcs, graphics, input_handler, bounds):
        self.player = player
        self.npcs = npcs
        self.graphics = graphics
        self.input = input_handler
        self.bounds = bounds
        self.running = True

    def run(self):
        while self.running:
            keys = self.input.get_keys()

            if "q" in keys:
                self.running = False

            self.player.update(keys, self.bounds)

            for npc in self.npcs:
                npc.update(self.bounds)

            self.graphics.render(self.player, self.npcs)
            time.sleep(0.1)