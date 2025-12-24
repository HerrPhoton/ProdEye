from typing import Any
from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True)
class MockDetectorConfig:
    """
    Параметры инициализации мокового детектора.

    :param class_ids: Набор возможных индексов классов.
    :type class_ids: Iterable[int]
    :param confidence_range: Диапазон уверенности детекции.
    :type confidence_range: tuple[float, float]
    :param detections_num_range: Диапазон количества детекций на кадре.
    :type detections_num_range: tuple[int, int]
    """
    class_ids: Iterable[int]
    confidence_range: tuple[float, float]
    detections_num_range: tuple[int, int]


def parse(raw: dict[str, Any]) -> MockDetectorConfig:
    """
    Создает экземпляр конфига мокового детектора :class:`MockDetectorConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфига.
    :type raw: dict[str, Any]
    :return: Экземпляр конфига, инициализированный параметрами из словаря.
    :rtype: MockDetectorConfig
    """
    return MockDetectorConfig(
        class_ids=raw.get("class_ids"),
        confidence_range=tuple(raw.get("confidence_range")),
        detections_num_range=tuple(raw.get("detections_num_range")),
    )
