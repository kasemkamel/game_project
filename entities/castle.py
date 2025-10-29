# entities/castle.py
import pygame
from entities.base_entity import BaseEntity

class Castle(BaseEntity):
    RADIUS = 10

    def draw(self, screen, camera):
        pos = camera.apply((self.x, self.y))
        pygame.draw.circle(screen, (50, 100, 255), pos, int(self.RADIUS * camera.zoom))
        pygame.draw.circle(screen, (0, 0, 120), pos, int(self.RADIUS * camera.zoom), 2)

    def is_clicked(self, pos):
        dx, dy = pos[0] - self.x, pos[1] - self.y
        return dx * dx + dy * dy <= self.RADIUS ** 2

    def __repr__(self):
        return "Castle"
