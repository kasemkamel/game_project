class Road:
    """طريق يربط بين كيانين (مثل مدينتين أو قلعة ومدينة)."""
    def __init__(self, start_entity, end_entity, speed_multiplier=1.5):
        self.start_entity = start_entity
        self.end_entity = end_entity
        self.speed_multiplier = speed_multiplier

    def get_length(self):
        """حساب طول الطريق (وهمي)."""
        # في التطبيق الحقيقي، سيتم استخدام إحداثيات الكيانات
        return 100

    def update(self):
        # صيانة الطريق
        pass
