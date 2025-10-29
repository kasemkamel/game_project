# entities/city.py
import pygame
from entities.base_entity import BaseEntity

class City(BaseEntity):
    RADIUS = 14

    def __init__(self, x, y, name="City"):
        super().__init__(x, y)
        self.name = name

    def draw(self, screen, camera):
        pos = camera.apply((self.x, self.y))
        pygame.draw.circle(screen, (0, 255, 0), pos, int(self.RADIUS * camera.zoom))
        pygame.draw.circle(screen, (0, 100, 0), pos, int(self.RADIUS * camera.zoom), 2)

    def is_clicked(self, pos):
        dx, dy = pos[0] - self.x, pos[1] - self.y
        return dx * dx + dy * dy <= self.RADIUS ** 2

    def __repr__(self):
        return f"City({self.name})"
