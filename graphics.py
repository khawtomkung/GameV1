class Graphics:
    def render(self, player, npcs):
        print("\033c", end="")  # clear terminal
        print("Player:", player.x, player.y)
        for i, npc in enumerate(npcs):
            print(f"NPC {i}:", npc.x, npc.y)
