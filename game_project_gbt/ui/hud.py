from .base_ui import BaseUI

class HUD(BaseUI):
    """
    شاشة العرض الرئيسية (Head-Up Display) التي تعرض معلومات اللعبة الأساسية.
    """
    def __init__(self, x, y, width, height, game_state=None):
        super().__init__(x, y, width, height)
        self.game_state = game_state

    def draw(self, screen):
        """رسم عناصر HUD مثل الموارد، الوقت، والرسائل."""
        if self.is_visible:
            print("  Drawing HUD: Resources, Time, etc.")
            # محاكاة عرض الموارد
            if self.game_state and hasattr(self.game_state, 'resource_system'):
                food = self.game_state.resource_system.get_total_resource("food")
                gold = self.game_state.resource_system.get_total_resource("gold")
                print(f"    Resources: Food={food}, Gold={gold}")
            super().draw(screen)

    def handle_input(self, event):
        """معالجة مدخلات المستخدم الخاصة بـ HUD (مثل النقر على زر القائمة)."""
        pass
