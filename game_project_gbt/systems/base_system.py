# game_project/systems/base_system.py

class BaseSystem:
    """
    الفئة الأساسية لجميع أنظمة اللعبة.
    """
    def __init__(self, game_state):
        self.game_state = game_state

    def update_20hz(self):
        """تحديث النظام بمعدل 20 هرتز (كل إطار)."""
        pass

    def update_per_4_min(self):
        """تحديث النظام بمعدل مرة كل 4دقائق)."""
        pass
