from .base_system import BaseSystem

class SpySystem(BaseSystem):
    """
    يتولى مسؤولية إدارة الجواسيس ومهامهم.
    """
    def __init__(self, game_state):
        super().__init__(game_state)

    def update_4_per_min(self):
        """تحديث مهام الجواسيس كل 15 ثانية."""
        print("SpySystem: Checking spy missions (4/min).")
        # منطق تنفيذ مهمة الجاسوس
        pass

    def send_spy(self, spy, target_entity, mission_type):
        """إرسال جاسوس في مهمة."""
        spy.assign_mission(mission_type, target_entity)
        print(f"SpySystem: Spy {spy.name} sent on mission {mission_type} to {target_entity.name}.")
