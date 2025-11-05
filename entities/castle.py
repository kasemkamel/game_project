# entities/castle.py
import pygame
from entities.base_entity import BaseEntity

class Castle(BaseEntity):
    RADIUS = 3
    

    def __init__(self, x, y, owner=None):
        super().__init__(x, y, owner)
        self.owner = owner
        self.garrison = set()

    def draw(self, screen, camera):
        pos = camera.apply((self.x, self.y))
        pygame.draw.circle(screen, (50, 100, 255), pos, int(self.RADIUS * camera.zoom))
        pygame.draw.circle(screen, (0, 0, 120), pos, int(self.RADIUS * camera.zoom), 2)

    def is_clicked(self, pos):
        dx, dy = pos[0] - self.x, pos[1] - self.y
        return dx * dx + dy * dy <= self.RADIUS ** 2
    
    def expelling_an_army(self, army):
        army.x = self.x + 10
        army.y = self.y + 10
        self.garrison.remove(army)
        army.is_visible = True
        army.target_entity = None
        army.city = None
    
    def expelling_first_army(self):
        army = self.garrison.pop()
        army.x = self.x + 10
        army.y = self.y + 10
        army.is_visible = True
        army.target_entity = None
        army.city = None

    def __repr__(self):
        return "Castle"

    def change_owner(self, new_owner):
        self.owner = new_owner
