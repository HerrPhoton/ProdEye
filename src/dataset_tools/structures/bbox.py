from dataclasses import dataclass


@dataclass
class BBox:
    class_id: int
    x: float
    y: float
    w: float
    h: float

    def validate(self, num_classes: int) -> bool:
        """
        Проверяет, находятся ли значения bbox в допустимом диапазоне.

        Для каждого bbox должны выполняться условия:
        1) Номер класса должен быть в диапазоне ``0..num_classes-1``
        2) Координаты и размеры bbox должны быть в диапазоне ``[0, 1]``

        :param num_classes: Количество классов в датасете ``0..num_classes-1``.
        :type num_classes: int
        :return: Являются ли значения bbox допустимыми.
        :rtype: bool
        """
        # Проверка координат (диапазон [0, 1])
        if not all(0 <= value <= 1 for value in (self.x, self.y, self.w, self.h)):
            return False

        # Проверка класса (диапазон [0, num_classes-1])
        if not 0 <= self.class_id < num_classes:
            return False

        return True
