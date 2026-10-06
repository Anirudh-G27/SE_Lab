import pygame


class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height

    def closest_point(self, px, py):
        """Return the point on (or inside) this wall's rectangle that is
        nearest to (px, py). Used for exact circle-vs-rectangle tests."""
        cx = min(max(px, self.left), self.right)
        cy = min(max(py, self.top), self.bottom)
        return cx, cy

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)