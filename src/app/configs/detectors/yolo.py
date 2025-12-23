from dataclasses import dataclass


@dataclass(frozen=True)
class YOLODetectorConfig:
    """
    Параметры инициализации детектора на базе YOLO.

    :var weights_path: Путь к модели YOLO.
    :vartype weights_path: str
    :var classes: Отображение индексов классов с их названиями.
    :vartype classes: dict[int, str]
    :var confidence_threshold: Минимальный порог уверенности детекции.
    :vartype confidence_threshold: float
    :var iou_threshold: Порог IoU для NMS.
    :vartype iou_threshold: float
    :var device: Целевое устройство для инференса.
    :vartype device: str
    """
    weights_path: str
    classes: dict[int, str]
    confidence_threshold: float
    iou_threshold: float
    device: str
