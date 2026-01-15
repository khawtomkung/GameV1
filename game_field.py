class GameField:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def clamp(self, x, y):
        return (max(self.x_min, min(self.x_max, x)), max(self.y_min, min(self.y_max, y)),
                self.x_min > x or self.x_max < x, self.y_min > y or self.y_max < y)
