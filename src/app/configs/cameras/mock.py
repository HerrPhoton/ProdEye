from dataclasses import dataclass


@dataclass(frozen=True)
class MockCameraConfig:
    """
    Параметры инициализации моковой камеры.

    :var width: Ширина кадра.
    :vartype width: int
    :var height: Высота кадра.
    :vartype height: int
    :var fps: Частота кадров.
    :vartype fps: int
    """
    width: int
    height: int
    fps: int
