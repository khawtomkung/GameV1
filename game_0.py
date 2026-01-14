# Real time game

import time
from pynput import keyboard

# from player import Player
# from npc import NPC
# from graphics import Graphics
from kb_poller import KBPoller
# from game_engine import GameEngine

bounds = {
    "x_min": 0,
    "x_max": 60,
    "y_min": 0,
    "y_max": 60,
}

# player = Player(10, 10)
# npcs = [NPC(50, 50, 1, 2)]

# graphics = Graphics()
input_kb = KBPoller()

# game = GameEngine(player, npcs, graphics, input_kb, bounds)
# game.run()