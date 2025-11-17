from collections import Counter

import numpy as np

from src.nn.detector import ProdDetector


class ProdMatcher:

    def __init__(self, detector: ProdDetector):
        self.detector = detector
        self.classes = detector.classes

    def get_class_counts(self, frame: np.ndarray) -> Counter:
        """Подсчитывает количество объектов каждого класса в кадре.

        :param np.ndarray frame: Кадр, на котором нужно произвети подсчет объектов
        :return Counter: Количество объектов каждого класса в кадре
        """
        detections = self.detector.predict(frame)
        if not detections:
            return Counter()

        detected_classes = detections[0].boxes.cls.cpu().numpy()
        class_names = [self.classes[int(idx)] for idx in detected_classes]

        return Counter(class_names)

    def is_match(self, selected_class: str, frame: np.ndarray, verified_count: int) -> bool:
        """Проверяет, есть ли в кадре новый объект выбранного класса.

        :param str selected_class: Название класса для проверки
        :param np.ndarray frame: Кадр
        :param int verified_count: Количество уже проверенных объектов этого класса
        """
        current_counts = self.get_class_counts(frame)
        return current_counts[selected_class] > verified_count
