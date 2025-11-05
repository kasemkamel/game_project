from .base_system import BaseSystem

class SpySystem(BaseSystem):
    """
    System responsible for managing and updating spy missions.
    """
    def __init__(self, game_state):
        super().__init__(game_state)

    def update_4_per_min(self):
        """update spy missions every 4 minutes."""
        print("SpySystem: Checking spy missions (4/min).")
        # Logic to execute spy missions
        pass

    def send_spy(self, spy, target_entity, mission_type):
        """Send a spy on a mission."""
        spy.assign_mission(mission_type, target_entity)
        print(f"SpySystem: Spy {spy.name} sent on mission {mission_type} to {target_entity.name}.")
