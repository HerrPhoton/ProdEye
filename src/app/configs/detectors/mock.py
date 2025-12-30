from typing import Any
from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True)
class MockDetectorConfig:
    """
    Параметры инициализации мокового детектора.

    :var class_ids: Набор возможных индексов классов.
    :vartype class_ids: Iterable[int]
    :var confidence_range: Диапазон уверенности детекции.
    :vartype confidence_range: tuple[float, float]
    :var detections_num_range: Диапазон количества детекций на кадре.
    :vartype detections_num_range: tuple[int, int]
    """
    class_ids: Iterable[int]
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
        class_ids=raw.get("class_ids"),
        confidence_range=tuple(raw.get("confidence_range")),
        detections_num_range=tuple(raw.get("detections_num_range")),
    )
