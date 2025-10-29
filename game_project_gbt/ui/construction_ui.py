from .base_ui import BaseUI

class ConstructionUI(BaseUI):
    """
    واجهة المستخدم الخاصة بالبناء في المدن والقلاع.
    """
    def __init__(self, x, y, width, height, game_state=None):
        super().__init__(x, y, width, height)
        self.game_state = game_state
        self.selected_entity = None

    def set_selected_entity(self, entity):
        """تعيين الكيان المحدد لعرض خيارات البناء."""
        self.selected_entity = entity
        self.is_visible = (entity is not None)

    def draw(self, screen):
        """رسم واجهة البناء."""
        if self.is_visible and self.selected_entity:
            print(f"  Drawing Construction UI for {self.selected_entity.name}")
            # رسم قائمة المباني المتاحة
            # رسم زر "بناء"
            super().draw(screen)

    def handle_input(self, event):
        """معالجة النقر على خيارات البناء."""
        if self.is_visible:
            # منطق معالجة النقر على زر البناء
            pass
