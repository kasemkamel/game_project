# entities/terrain.py
import pygame
from shapely.geometry import Polygon as pol, Point


class terrain:
    def __init__(self, points, color):
        self.points = points
        self.color = color
        self.polygon = pol(points)

    def containsPoint(self, point):
        return self.polygon.contains(Point(point))

    
    def containsXY(self, x, y):
        return self.polygon.contains(Point(x, y))
    
    def draw(self, screen, camera):
        scaled_points = [camera.apply(p) for p in self.points]
        pygame.draw.polygon(screen, self.color, scaled_points)
        pygame.draw.polygon(screen, (40, 40, 40), scaled_points, 1)  # Border
