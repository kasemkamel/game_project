# entities/base_entity.py
import pygame
class BaseEntity:
    def __init__(self, x, y, owner=None):
        self.x = x
        self.y = y
        self.owner = owner

    def is_clicked(self, pos):
        raise NotImplementedError
    
    def get_available_actions(self):
        raise NotImplementedError

    def draw(self, screen, camera):
        scaled_points = [camera.apply(p) for p in self.points]
        pygame.draw.polygon(screen, self.color, scaled_points)
        pygame.draw.polygon(screen, (40, 40, 40), scaled_points, 1)  # Border
    