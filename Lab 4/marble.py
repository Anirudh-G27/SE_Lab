import pygame


class Marble:
    def __init__(self, x, y, radius=12):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0
        self.vy = 0

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0

    def rect(self):
        # Bounding box only (kept for compatibility). Collision detection
        # uses the true circle, not this rectangle.
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)