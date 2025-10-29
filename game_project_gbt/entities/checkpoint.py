# entities/checkpoint.py
import pygame
from entities.base_entity import BaseEntity

class Checkpoint(BaseEntity):
    RADIUS = 6

    def draw(self, screen, camera):
        pos = camera.apply((self.x, self.y))
        pygame.draw.circle(screen, (240, 220, 60), pos, int(self.RADIUS * camera.zoom))
        pygame.draw.circle(screen, (120, 100, 30), pos, int(self.RADIUS * camera.zoom), 1)

    def is_clicked(self, pos):
        dx, dy = pos[0] - self.x, pos[1] - self.y
        return dx * dx + dy * dy <= self.RADIUS ** 2

    def __repr__(self):
        return "Checkpoint"
