from typing import Any

from src.app.configs.cameras import MockCameraConfig, OpenCVCameraConfig
from src.app.configs.cameras.mock import parse as parse_mock
from src.app.configs.cameras.opencv import parse as parse_opencv

CameraConfig = MockCameraConfig | OpenCVCameraConfig

def parse_camera(raw_data: dict[str, Any]) -> CameraConfig:
    """
    Возвращает экземпляр конфигурации камеры в зависимости от
    типа переданной конфигурации по ключу ``"type"``.

    :param raw_data: Словарь с параметрами камеры.
    :type raw_data: dict[str, Any]
    :raises TypeError: Если тип конфигурации не соответвует допустимому.
    :return: Экземпляр конфигурации камеры.
    :rtype: CameraConfig
    """
    data_copy = raw_data.copy()
    type = data_copy.pop("type")

    match type:
        case "opencv":
            return parse_opencv(data_copy)

        case "mock":
            return parse_mock(data_copy)

        case _:
            raise TypeError(
                f"Invalid camera configuration type: {type}. "
                f"Allowed: mock, opencv."
            )
