# core/renderer.py
import pygame
from ui.tooltip import Tooltip

class Renderer: 
    def __init__(self,game, screen, camera):
        self.game=game
        self.screen = screen
        self.camera = camera
        self.map_image = pygame.image.load("assets/maps/map_model_v8.png").convert()
        self.base_map = self.map_image.copy()
        self.tooltip = Tooltip()
    
    def render_debug_mode(self, provinces, cities, castles, checkpoints, armies, mountains, rivers, selected_army=None):
        self.screen.fill((25, 25, 35))
        for m in mountains:
            m.draw(self.screen, self.camera)
        for r in rivers:
            r.draw(self.screen, self.camera)
        for p in provinces:
            p.draw(self.screen, self.camera)
        for c in cities:
            c.draw(self.screen, self.camera)
        for c in castles:
            c.draw(self.screen, self.camera)
        for cp in checkpoints:
            cp.draw(self.screen, self.camera)
        for a in armies:
            a.draw(self.screen, self.camera, is_selected=(a == selected_army))

    def render_image_mode(self, cities, castles, checkpoints, armies, selected_army=None):
        width = int(self.base_map.get_width() * self.camera.zoom)
        height = int(self.base_map.get_height() * self.camera.zoom)
        scaled_map = pygame.transform.smoothscale(self.base_map, (width, height))
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_map, (-self.camera.x * self.camera.zoom, -self.camera.y * self.camera.zoom))
        
        for c in cities:
            c.draw(self.screen, self.camera)
        for c in castles:
            c.draw(self.screen, self.camera)
        for a in armies:
            a.draw(self.screen, self.camera, is_selected=(a == selected_army))
        for cp in checkpoints:
            cp.draw(self.screen, self.camera)
            
        if self.game.input.hovered_entity:
            mouse_pos = pygame.mouse.get_pos()
            self.tooltip.update(self.game.input.hovered_entity, mouse_pos)
            self.tooltip.render(self.screen)
        else:
            self.tooltip.hide()


