from .base_ui import BaseUI

class HUD(BaseUI):
    """
    HUD (Heads-Up Display) component for displaying game information.
    """
    def __init__(self, x, y, width, height, game_state=None):
        super().__init__(x, y, width, height)
        self.game_state = game_state

    def draw(self, screen):
        """Draw HUD elements such as resources, time, and messages."""
        if self.is_visible:
            print("  Drawing HUD: Resources, Time, etc.")
            # Simulate drawing resources
            if self.game_state and hasattr(self.game_state, 'resource_system'):
                food = self.game_state.resource_system.get_total_resource("food")
                gold = self.game_state.resource_system.get_total_resource("gold")
                print(f"    Resources: Food={food}, Gold={gold}")
            super().draw(screen)

    def handle_input(self, event):
        """Handle user input for the HUD (e.g., clicking on menu buttons)."""
        pass
