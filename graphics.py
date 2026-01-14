class Graphics:
    def render(self, player, npcs):
        print("Player:", player.x, player.y)

        for i, npc in enumerate(npcs):
            print(f"NPC {i}:", npc.x, npc.y)