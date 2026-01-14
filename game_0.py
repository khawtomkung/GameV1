# Real time game

import time
from pynput import keyboard


class KBPoller:
    def on_press(self, key):
        try:
            ch = key.char.lower()
            self.pressed.add(ch)
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            ch = key.char.lower()
            self.pressed.remove(ch)
        except AttributeError:
            pass

    def __init__(self):
        self.pressed = set()

        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

running = True

player_x = 10
player_y = 10

npc_x = 50
npc_y = 50
npc_speed_x = 1
npc_speed_y = 2

x_min = 0
x_max = 60
y_min = 0
y_max = 60

kb = KBPoller()

def scan_keys():
    return kb.pressed

def render_state():
    print("player is at:", player_x, player_y)
    print("npc is at:", npc_x, npc_y)

def update_state(keys):
    global player_x, player_y, running, npc_x, npc_y, npc_speed_x, npc_speed_y

    
    npc_x += npc_speed_x
    npc_y += npc_speed_y

    if npc_x > x_max or npc_x < x_min:
        npc_speed_x = -npc_speed_x
    if npc_y > y_max or npc_y < y_min:
        npc_speed_y = -npc_speed_y

    if "a" in keys:
        player_x -= 1
    if "d" in keys:
        player_x += 1
    if "w" in keys:
        player_y -= 1
    if "s" in keys:
        player_y += 1
    if "q" in keys:
        running = False

    if player_x < x_min:
        player_x = x_min
    if player_x > x_max:
        player_x = x_max
    if player_y < y_min:
        player_y = y_min
    if player_y > y_max:
        player_y = y_max

while running:
    # read/check for user actions (input)
    # update game state (physics, AI, etc)
    # render game state (graphics)

    render_state()
    keys = scan_keys()

    update_state(keys)

    time.sleep(0.1)