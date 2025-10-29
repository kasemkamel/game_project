# core/renderer.py
import pygame

class Renderer:
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera

    def render(self, provinces, cities, castles, checkpoints, armies):
        self.screen.fill((25, 25, 35))
        for p in provinces:
            p.draw(self.screen, self.camera)
        for c in cities:
            c.draw(self.screen, self.camera)
        for c in castles:
            c.draw(self.screen, self.camera)
        for cp in checkpoints:
            cp.draw(self.screen, self.camera)
        for a in armies:
            a.draw(self.screen, self.camera)
