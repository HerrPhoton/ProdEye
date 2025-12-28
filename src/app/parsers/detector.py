from typing import Any

from src.app.configs.detectors import MockDetectorConfig, YOLODetectorConfig
from src.app.configs.detectors.mock import parse as parse_mock
from src.app.configs.detectors.yolo import parse as parse_yolo

DetectorConfig = MockDetectorConfig | YOLODetectorConfig

def parse_detector(raw_data: dict[str, Any]) -> DetectorConfig:
    """
    Возвращает экземпляр конфигурации детектора в зависимости от
    типа переданной конфигурации по ключу ``"type"``.

    :param raw_data: Словарь с параметрами детектора.
    :type raw_data: dict[str, Any]
    :raises TypeError: Если тип конфигурации не соответвует допустимому.
    :return: Экземпляр конфигурации детектора.
    :rtype: DetectorConfig
    """
    data_copy = raw_data.copy()
    type = data_copy.pop("type")

    match type:
        case "yolo":
            return parse_yolo(data_copy)

        case "mock":
            return parse_mock(data_copy)

        case _:
            raise TypeError(
                f"Invalid camera configuration type: {type}. "
                f"Allowed: mock, opencv."
            )
