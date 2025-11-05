from .base_entity import BaseEntity
from enum import Enum

class Rarity(Enum):
    COMMON = 1
    uNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5

class Commander(BaseEntity):
    """Commander entity that leads armies and undertakes missions"""
    def __init__(self, name, owner=None, rarity: Rarity = Rarity.COMMON):
        super().__init__(0, 0, name)
        self.rarity = rarity
        self.mission = None
        self.target_entity = None
        self.owner = owner

    def assign_mission(self, mission_type, target):
        pass

    def update(self):
        # Update mission logic
        pass

    def __repr__(self):
        return f"Commander({self.name}, Rarity: {self.rarity.name}, Mission: {self.mission})"
