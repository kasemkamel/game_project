# entities/army.py
import pygame
from entities.base_entity import BaseEntity

class Army(BaseEntity):
    RADIUS = 8
    SPEED = 30  # pixels/sec

    def __init__(self, x, y):
        super().__init__(x, y)
        self.destination = None

    def update(self, dt):
        if self.destination:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            dist = (dx**2 + dy**2) ** 0.5
            if dist < 1:
                self.destination = None
                return
            nx, ny = dx / dist, dy / dist
            self.x += nx * self.SPEED * dt
            self.y += ny * self.SPEED * dt

    def draw(self, screen, camera):
        pos = camera.apply((self.x, self.y))
        pygame.draw.circle(screen, (255, 255, 255), pos, int(self.RADIUS * camera.zoom))
        pygame.draw.circle(screen, (100, 100, 100), pos, int(self.RADIUS * camera.zoom), 1)

    def is_clicked(self, pos):
        dx, dy = pos[0] - self.x, pos[1] - self.y
        return dx * dx + dy * dy <= self.RADIUS ** 2

    def __repr__(self):
        return "Army"
