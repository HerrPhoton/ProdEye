from typing import TypeAlias

from src.adapters.cameras import MockCamera, OpenCVCamera
from src.core.ports.camera import Camera
from src.app.configs.cameras import MockCameraConfig, OpenCVCameraConfig

CameraConfig: TypeAlias = MockCameraConfig | OpenCVCameraConfig

def build_camera(config: CameraConfig) -> Camera:
    """
    Возвращает экземпляр камеры в зависимости от
    типа переданной конфигурации.

    :param config: Конфигурация камеры.
    :type config: CameraConfig
    :raises TypeError: Если тип конфигурции не соответвует допустимому.
    :return: Экзепляр камеры, инициализированный конфигурацией.
    :rtype: Camera
    """
    if isinstance(config, MockCameraConfig):
        return MockCamera(config)

    if isinstance(config, OpenCVCameraConfig):
        return OpenCVCamera(config)

    raise TypeError(
        f"Invalid configuration type: {type(config)}. "
        f"Allowed: MockCameraConfig, OpenCVCameraConfig."
    )
