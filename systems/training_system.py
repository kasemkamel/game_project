from .base_system import BaseSystem

class TrainingSystem(BaseSystem):
    """
    System responsible for managing and updating unit training queues.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.training_queues = {} # {entity_id: [unit_type, quantity, time_remaining]}

    def update_4_per_min(self):
        """update training queues every 4 minutes."""
        print("TrainingSystem: Processing training queues (4/min).")
        # Logic to reduce training time and add completed units
        pass

    def start_training(self, entity, unit_type, quantity):
        """Start training new units at a specific entity."""
        # Dummy logic for starting training
        training_time = quantity * 2  # e.g., 2 minutes per unit
        print(f"TrainingSystem: Started training {quantity} of {unit_type} at {entity.name}.")
        self.training_queues[entity.id] = [unit_type, quantity, training_time]
