# core/camera.py
class Camera:
    def __init__(self, width, height):
        self.x, self.y = 0, 0
        self.zoom = 1.0
        self.width = width
        self.height = height

    def apply(self, pos):
        return ((pos[0] - self.x) * self.zoom, (pos[1] - self.y) * self.zoom)

    def screen_to_world(self, pos):
        return (pos[0] / self.zoom + self.x, pos[1] / self.zoom + self.y)

    def move(self, dx, dy):
        self.x += dx / self.zoom
        self.y += dy / self.zoom

    def zoom_in(self):
        self.zoom = min(self.zoom * 1.1, 3.0)

    def zoom_out(self):
        self.zoom = max(self.zoom / 1.1, 0.5)
