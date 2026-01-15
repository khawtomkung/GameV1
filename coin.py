class Coin:
    def __init__(self, x, y, radius=8):
        self.x = x
        self.y = y
        self.radius = radius
        self.collected = False

    def check_collision(self, player_x, player_y, player_radius):
        dx = self.x - player_x
        dy = self.y - player_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance < (self.radius + player_radius)