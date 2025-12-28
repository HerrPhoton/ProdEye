from typing import TypeAlias

from src.adapters.detectors import MockDetector, YOLODetector
from src.core.ports.detector import Detector
from src.app.configs.detectors import MockDetectorConfig, YOLODetectorConfig

DetectorConfig: TypeAlias = MockDetectorConfig | YOLODetectorConfig

def build_detector(config: DetectorConfig) -> Detector:
    """
    Возвращает экземпляр детектора в зависимости от
    типа переданной конфигурации.

    :param config: Конфигурация детектора.
    :type config: DetectorConfig
    :raises TypeError: Если тип Конфигурации не соответвует допустимому.
    :return: Экзепляр детектора, инициализированный конфигурацией
    :rtype: Detector
    """
    if isinstance(config, MockDetectorConfig):
        return MockDetector(config)

    if isinstance(config, YOLODetectorConfig):
        return YOLODetector(config)

    raise TypeError(
        f"Invalid configuration type: {type(config)}. "
        f"Allowed: MockDetectorConfig, YOLODetectorConfig."
    )
