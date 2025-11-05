# game_project/systems/base_system.py

class BaseSystem:
    """
    base system class for game systems.
    """
    def __init__(self, game_state):
        self.game_state = game_state

    def update_20hz(self):
        """update the system at 20Hz (20 times per second)."""
        pass

    def update_per_4_min(self):
        """update the system every 4 minutes."""
        pass
