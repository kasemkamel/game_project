# game_project/ui/base_ui.py

class BaseUI:
    """
    الفئة الأساسية لعناصر واجهة المستخدم.
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_visible = True

    def draw(self, screen):
        """رسم عنصر واجهة المستخدم على الشاشة."""
        if self.is_visible:
            # منطق الرسم الوهمي
            print(f"  Drawing {self.__class__.__name__} at ({self.x}, {self.y})")

    def handle_input(self, event):
        """معالجة مدخلات المستخدم الخاصة بعنصر واجهة المستخدم."""
        pass
