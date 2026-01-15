# Real time game

import time

from pygame_input_controller import PygameInputController
from player import Player
from npc import NPC
from game_field import GameField
from graphics import GraphicsEngine
from game_engine import GameEngine

if __name__ == "__main__":
    game_field = GameField(0, 0, 500, 500)
    player = Player(50, 50)
    npc = NPC(70, 70, 2, 1)

    graphics = GraphicsEngine(500, 500)
    input_controller = PygameInputController()

    game_engine = GameEngine(
        graphics,
        input_controller,
        game_field,
        player,
        npc,
        fps=165
    )

    game_engine.run_game()