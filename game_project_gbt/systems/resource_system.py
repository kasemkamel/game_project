from .base_system import BaseSystem

class ResourceSystem(BaseSystem):
    """
    يتولى مسؤولية إنتاج واستهلاك الموارد في جميع المقاطعات.
    """
    def __init__(self, game_state):
        super().__init__(game_state)

    def update_4_per_min(self):
        """تحديث الموارد كل 15 ثانية."""
        print("ResourceSystem: Calculating resource production and consumption (4/min).")
        # منطق تحديث الموارد لكل مقاطعة
        if self.game_state and hasattr(self.game_state, 'provinces'):
            for province in self.game_state.provinces:
                # محاكاة إنتاج الموارد
                province.resources["food"] += 5
                province.resources["wood"] += 2
                print(f"  Province {province.name} now has {province.resources['food']} food.")
        pass

    def get_total_resource(self, resource_type):
        """حساب إجمالي مورد معين في جميع المقاطعات."""
        total = 0
        if self.game_state and hasattr(self.game_state, 'provinces'):
            for province in self.game_state.provinces:
                total += province.resources.get(resource_type, 0)
        return total
