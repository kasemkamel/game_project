# entity/spy.py
from .assestent import Assestant, AssestantState # READY, ON_MISSION, TRAVELING

class Spy(Assestant):
    """Spy entity that gathers intelligence."""
    def __init__(self, x, y, name, owner, skill_level=1):
        super().__init__(x, y, name, owner, skill_level)
        self.state = AssestantState.READY
        self.mission = None
        self.target_entity = None

    def update(self):
        pass

    def __repr__(self):
        return f"Spy({self.name}, Skill: {self.skill_level}, Mission: {self.mission})"
    