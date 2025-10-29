# entities/base_entity.py
class BaseEntity:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_clicked(self, pos):
        raise NotImplementedError

    def draw(self, screen, camera):
        raise NotImplementedError
    