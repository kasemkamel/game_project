from .base_system import BaseSystem

class HappinessSystem(BaseSystem):
    """
    System responsible for managing and updating the happiness levels of provinces.
    """
    def __init__(self, game_state):
        super().__init__(game_state)

    def update_4_per_min(self):
        """update happiness every 4 minutes."""
        print("HappinessSystem: Recalculating province happiness (4/min).")
        # Logic to update happiness based on factors like resources, population, and military
        if self.game_state and hasattr(self.game_state, 'provinces'):
            for province in self.game_state.provinces:
                # Simulate a slight increase in happiness
                province.happiness = min(1.0, province.happiness + 0.01)
                print(f"  Province {province.name} happiness: {province.happiness:.2f}")
        pass
