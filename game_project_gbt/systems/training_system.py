from .base_system import BaseSystem

class TrainingSystem(BaseSystem):
    """
    يتولى مسؤولية تدريب الوحدات العسكرية في القلاع والمدن.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.training_queues = {} # {entity_id: [unit_type, quantity, time_remaining]}

    def update_4_per_min(self):
        """تحديث صفوف التدريب كل 15 ثانية."""
        print("TrainingSystem: Processing training queues (4/min).")
        # منطق تقليل وقت التدريب وإضافة الوحدات المكتملة
        pass

    def start_training(self, entity, unit_type, quantity):
        """بدء تدريب وحدات جديدة في كيان معين."""
        # منطق وهمي
        print(f"TrainingSystem: Started training {quantity} of {unit_type} at {entity.name}.")
        # self.training_queues[entity.id] = [unit_type, quantity, training_time]
