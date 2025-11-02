from .base_entity import BaseEntity

class Spy(BaseEntity):
    """وحدة تجسس."""
    def __init__(self, x, y, name, skill_level=1, owner=None):
        super().__init__(x, y, name)
        self.skill_level = skill_level
        self.mission = None
        self.target_entity = None
        self.owner = owner

    def assign_mission(self, mission_type, target):
        self.mission = mission_type
        self.target_entity = target

    def update(self):
        # منطق تنفيذ المهمة
        pass
    
    def __repr__(self):
        return f"Spy({self.name}, Skill: {self.skill_level}, Mission: {self.mission})"
    
    def change_owner(self, new_owner):
        self.owner = new_owner
