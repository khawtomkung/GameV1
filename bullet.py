class Bullet:
    def __init__(self, x, y, direction, speed=8, radius=5):
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        
        # กำหนดความเร็วตามทิศทาง
        self.vx = 0
        self.vy = 0
        if direction == "up":
            self.vy = -speed
        elif direction == "down":
            self.vy = speed
        elif direction == "left":
            self.vx = -speed
        elif direction == "right":
            self.vx = speed

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def is_out_of_bounds(self, game_field):
        return (self.x < game_field.x_min - 50 or 
                self.x > game_field.x_max + 50 or
                self.y < game_field.y_min - 50 or 
                self.y > game_field.y_max + 50)

    def check_collision(self, other_x, other_y, other_radius):
        dx = self.x - other_x
        dy = self.y - other_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance < (self.radius + other_radius)