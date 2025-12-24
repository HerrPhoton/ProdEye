from typing import Any
from dataclasses import dataclass

from src.utils import normalize_class_mapping


@dataclass(frozen=True)
class YOLODetectorConfig:
    """
    Параметры инициализации детектора на базе YOLO.

    :var weights_path: Путь к модели YOLO.
    :vartype weights_path: str
    :var classes: Отображение индексов классов с их названиями.
    :vartype classes: dict[int, str]
    :var confidence_threshold: Минимальный порог уверенности детекции.
    :vartype confidence_threshold: float, optional
    :var iou_threshold: Порог IoU для NMS.
    :vartype iou_threshold: float, optional
    :var device: Целевое устройство для инференса.
    :vartype device: str, optional
    """
    weights_path: str
    classes: dict[int, str]
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.7
    device: str = "cpu"


def parse(raw: dict[str, Any]) -> YOLODetectorConfig:
    """
    Создает экземпляр конфига детектора :class:`YOLODetectorConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфига.
    :type raw: dict[str, Any]
    :return: Экземпляр конфига, инициализированный параметрами из словаря.
    :rtype: YOLODetectorConfig
    """
    thresholds = raw.get("thresholds", {})
    return YOLODetectorConfig(
        weights_path=raw["weights_path"],
        classes=normalize_class_mapping(raw["classes"]),
        confidence_threshold=thresholds.get("confidence", 0.25),
        iou_threshold=thresholds.get("iou", 0.7),
        device=raw.get("device", "cpu"),
    )
