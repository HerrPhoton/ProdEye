import numpy as np
from ultralytics import YOLO

from src.core.dto import Detection
from src.app.configs.detectors import YOLODetectorConfig


class YOLODetector:
    """Детектор объектов на базе YOLO."""

    def __init__(self, config: YOLODetectorConfig):
        self.model = YOLO(config.weights_path)
        self.class_ids = list(config.classes)
        self.conf_threshold = config.confidence_threshold
        self.iou_threshold = config.iou_threshold
        self.device = config.device

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Выполняет детекцию объектов на видеокадре.

        :param frame: Видеокадр.
        :type frame: np.ndarray
        :return: Список детекций на видеокадре.
        :rtype: list[Detection]
        """
        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )

        detections: list[Detection] = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                class_id = int(box.cls.item())
                confidence = float(box.conf.item())

                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                detections.append(
                    Detection(
                        class_id=class_id,
                        confidence=confidence,
                        bbox=(x1, y1, x2, y2),
                    )
                )

        return detections
