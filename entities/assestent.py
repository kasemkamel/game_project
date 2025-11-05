# entity/assestent.py
from .base_entity import BaseEntity
from enum import Enum

class AssestantState(Enum):
    READY = 1
    ON_MISSION = 2
    TRAVELING = 3

class Assestant(BaseEntity):
    """Assestant entity that supports armies and missions"""
    def __init__(self, x, y, name, owner, skill_level=1):
        super().__init__(x, y, name)
        self.skill_level = skill_level
        self.state = AssestantState.READY
        self.mission = None
        self.target_entity = None
        self.owner = owner
        self.coverage_points = 0

    def assign_mission(self, mission, target_entity):
        self.mission = mission
        self.target_entity = target_entity
        self.state = AssestantState.ON_MISSION

    def level_up(self):
        self.skill_level += 1
        self.update_missions(self)

    def update_coverage(self):
        self.coverage_points += ((self.skill_level - 1) // 2 + 1) # Increase coverage based on skill level (1-5 points per slow tick)

    def update(self):
        if self.state == AssestantState.READY:
            self.update_coverage()
        elif self.state == AssestantState.ON_MISSION:
            self.mission.execute(self)
        elif self.state == AssestantState.TRAVELING:
            # set coverage to 0
            self.coverage_points = 0
    
    def __repr__(self):
        return f"Assestant({self.name}, Skill: {self.skill_level}, Mission: {self.mission})"