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
