import numpy as np

from .detector import ProdDetector


class ProdMatcher:

    def __init__(self, detector: ProdDetector):
        self.detector = detector
        self.classes = detector.classes

    def is_match(self, selected_class: str, frame: np.ndarray) -> bool:
        class_id = None
        for idx, name in self.classes.items():
            if name == selected_class:
                class_id = idx
                break

        if class_id is None:
            raise ValueError(f"Продукт '{selected_class}' отсутствует в списке.")

        detections = self.detector.predict(frame)

        if not detections:
            return False

        detected_classes = detections[0].boxes.cls.cpu().numpy()
        return class_id in detected_classes
