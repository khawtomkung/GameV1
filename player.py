class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, keys, bounds):
        if "a" in keys:
            self.x -= 1
        if "d" in keys:
            self.x += 1
        if "w" in keys:
            self.y -= 1
        if "s" in keys:
            self.y += 1

        self.x = max(bounds["x_min"], min(self.x, bounds["x_max"]))
        self.y = max(bounds["y_min"], min(self.y, bounds["y_max"]))
