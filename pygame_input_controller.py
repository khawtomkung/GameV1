import pygame

class PygameInputController:
    def __init__(self):
        pass

    def get_pressed_keys(self):
        keys = pygame.key.get_pressed()
        pressed = set()

        if keys[pygame.K_a]:
            pressed.add("a")
        if keys[pygame.K_d]:
            pressed.add("d")
        if keys[pygame.K_w]:
            pressed.add("w")
        if keys[pygame.K_s]:
            pressed.add("s")
        if keys[pygame.K_q]:
            pressed.add("q")

        return pressed