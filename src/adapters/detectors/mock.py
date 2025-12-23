import random

import numpy as np

from src.core.dto import Detection
from src.app.configs.detectors import MockDetectorConfig


class MockDetector:
    """Моковый детектор объектов."""

    def __init__(self, config: MockDetectorConfig):
        self.class_ids = config.class_ids
        self.confidence_range = config.confidence_range
        self.detections_num_range = config.detections_num_range

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Возвращает фиктивные детекции для видеокадра.

        :param frame: Видеокадр.
        :type frame: np.ndarray
        :return: Список фиктивных детекций на видеокадре.
        :rtype: list[Detection]
        """
        h, w = frame.shape[:2]
        detections_num = random.randint(*self.detections_num_range)

        return [
            Detection(
                class_id=random.choice(self.class_ids),
                confidence=random.uniform(*self.confidence_range),
                bbox=self._random_bbox(w, h),
            )
            for _ in range(detections_num)
        ]

    @staticmethod
    def _random_bbox(width: int, height: int) -> tuple[int, int, int, int]:
        """
        Генерирует случайный bbox для кадра.

        :param width: Ширина кадра.
        :type width: int
        :param height: Высота кадра.
        :type height: int
        :return: Координаты bbox'а ``(x1, y1, x2, y2)``.
        :rtype: tuple[int, int, int, int]
        """
        x1 = random.randint(0, width - 1)
        y1 = random.randint(0, height - 1)
        x2 = random.randint(x1 + 1, width)
        y2 = random.randint(y1 + 1, height)

        return x1, y1, x2, y2
