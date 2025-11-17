from dataclasses import dataclass


@dataclass
class BBox:
    class_id: int
    x: float
    y: float
    w: float
    h: float

    def validate(self, num_classes: int) -> bool:
        """Проверяет, находятся ли значения bbox в допустимом диапазоне.

        :param int num_classes: Количество классов в датасете (классы: 0..num_classes-1)
        :return bool: Являются ли значения bbox допустимыми
        """
        # Проверка координат (диапазон [0, 1])
        if not all(0 <= value <= 1 for value in (self.x, self.y, self.w, self.h)):
            return False

        # Проверка класса (диапазон [0, num_classes-1])
        if not 0 <= self.class_id < num_classes:
            return False

        return True
