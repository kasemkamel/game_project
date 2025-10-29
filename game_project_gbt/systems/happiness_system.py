from .base_system import BaseSystem

class HappinessSystem(BaseSystem):
    """
    يتولى مسؤولية حساب وتحديث مستوى السعادة في المقاطعات.
    """
    def __init__(self, game_state):
        super().__init__(game_state)

    def update_4_per_min(self):
        """تحديث السعادة كل 15 ثانية."""
        print("HappinessSystem: Recalculating province happiness (4/min).")
        # منطق تحديث السعادة بناءً على عوامل مثل الموارد، السكان، والجيش
        if self.game_state and hasattr(self.game_state, 'provinces'):
            for province in self.game_state.provinces:
                # محاكاة زيادة طفيفة في السعادة
                province.happiness = min(1.0, province.happiness + 0.01)
                print(f"  Province {province.name} happiness: {province.happiness:.2f}")
        pass
