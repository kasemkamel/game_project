from shapely import length


class Road:
    """road entity connecting two entities, used for trade and supply lines."""
    def __init__(self, start_entity, end_entity, speed_multiplier=1.5):
        self.start_entity = start_entity
        self.end_entity = end_entity
        self.speed_multiplier = speed_multiplier
        self.length = self.get_length()

    def get_length(self):
        """Calculate road length between start and end entities"""
        dx = self.end_entity.x - self.start_entity.x
        dy = self.end_entity.y - self.start_entity.y
        length = (dx * dx + dy * dy) ** 0.5
        return length

    def update(self):
        # Road maintenance and other updates
        pass
