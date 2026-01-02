from typing import Any
from dataclasses import dataclass

from src.utils import normalize_class_mapping


@dataclass(frozen=True)
class MockDetectorConfig:
    """
    Параметры инициализации мокового детектора.

    :var classes: Отображение индексов классов с их названиями.
    :vartype classes: dict[int, str]
    :var confidence_range: Диапазон уверенности детекции.
    :vartype confidence_range: tuple[float, float]
    :var detections_num_range: Диапазон количества детекций на кадре.
    :vartype detections_num_range: tuple[int, int]
    """
    classes: dict[int, str]
    confidence_range: tuple[float, float]
    detections_num_range: tuple[int, int]


def parse(raw: dict[str, Any]) -> MockDetectorConfig:
    """
    Создает экземпляр конфигурации мокового детектора :class:`MockDetectorConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфигурации.
    :type raw: dict[str, Any]
    :return: Экземпляр конфигурации, инициализированный параметрами из словаря.
    :rtype: MockDetectorConfig
    """
    return MockDetectorConfig(
        classes=normalize_class_mapping(raw["classes"]),
        confidence_range=tuple(raw["confidence_range"]),
        detections_num_range=tuple(raw["detections_num_range"]),
    )
