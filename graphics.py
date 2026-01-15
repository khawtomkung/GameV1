import pygame

class GraphicsEngine:
    def __init__(self, width=600, height=600):
        pygame.init()

        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Simple Game")

        self.clock = pygame.time.Clock()

    def start_frame(self):
        self.screen.fill((0, 0, 0))  # black background

        # handle window close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def show_frame(self):
        pygame.display.flip()

    def render_circle(self, x, y, radius, color):
        colors = {
            "red": (255, 0, 0),
            "blue": (0, 0, 255)
        }

        pygame.draw.circle(
            self.screen,
            colors.get(color, (225, 225, 225)),
            (int(x), int(y)),
            radius
        )