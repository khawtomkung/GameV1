class NPC:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self, bounds):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= bounds["x_min"] or self.x >= bounds["x_max"]:
            self.speed_x *= -1
        if self.y <= bounds["y_min"] or self.y >= bounds["y_max"]:
            self.speed_y *= -1
