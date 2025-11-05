# game_project/ui/base_ui.py

class BaseUI:
    """
    base class for UI elements.
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_visible = True

    def draw(self, screen):
        """Draw the UI element on the screen."""
        if self.is_visible:
            # Drawing logic here
            print(f"  Drawing {self.__class__.__name__} at ({self.x}, {self.y})")

    def handle_input(self, event):
        """Handle user input for the UI element."""
        pass
