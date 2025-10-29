# entities/province.py
import pygame

class Province:
    def __init__(self, points, color):
        self.points = points
        self.color = color

    def draw(self, screen, camera):
        scaled_points = [camera.apply(p) for p in self.points]
        pygame.draw.polygon(screen, self.color, scaled_points)
        pygame.draw.polygon(screen, (40, 40, 40), scaled_points, 2)
