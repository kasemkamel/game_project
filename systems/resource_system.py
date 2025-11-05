from .base_system import BaseSystem

class ResourceSystem(BaseSystem):
    """
    System responsible for managing and updating resource production and consumption.
    """
    def __init__(self, game_state):
        super().__init__(game_state)

    def update_4_per_min(self):
        """update resources every 4 minutes."""
        print("ResourceSystem: Calculating resource production and consumption (4/min).")
        # Logic to update resources for each province
        if self.game_state and hasattr(self.game_state, 'provinces'):
            for province in self.game_state.provinces:
                # Simulate resource production
                province.resources["food"] += 5
                province.resources["wood"] += 2
                print(f"  Province {province.name} now has {province.resources['food']} food.")
        pass

    def get_total_resource(self, resource_type):
        """Calculate the total amount of a specific resource across all provinces."""
        total = 0
        if self.game_state and hasattr(self.game_state, 'provinces'):
            for province in self.game_state.provinces:
                total += province.resources.get(resource_type, 0)
        return total
