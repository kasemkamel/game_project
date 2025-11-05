from .base_ui import BaseUI

class ConstructionUI(BaseUI):
    """
    UI component for managing construction options for selected entities.
    """
    def __init__(self, x, y, width, height, game_state=None):
        super().__init__(x, y, width, height)
        self.game_state = game_state
        self.selected_entity = None

    def set_selected_entity(self, entity):
        """Set the selected entity to display construction options."""
        self.selected_entity = entity
        self.is_visible = (entity is not None)

    def draw(self, screen):
        """Draw the construction UI."""
        if self.is_visible and self.selected_entity:
            print(f"  Drawing Construction UI for {self.selected_entity.name}")
            # Draw the list of available buildings
            # Draw the "Build" button
            super().draw(screen)

    def handle_input(self, event):
        """Handle input for construction options."""
        if self.is_visible:
            # Handle click on build button
            pass
