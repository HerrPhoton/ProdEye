from dataclasses import dataclass


@dataclass
class CameraConfig:
    """
    Параметры инициализации камеры.

    :var source: Индекс камеры или путь до источника видео.
    :vartype source: int | str, optional
    :var width: Целевая ширина кадра.
    :vartype width: int | None, optional
    :var height: Целевая высота кадра.
    :vartype height: int | None, optional
    :var fps: Целевая частота кадров.
    :vartype fps: int | None, optional
    :var convert_to_rgb: Конвертировать ли BGR в RGB.
    :vartype convert_to_rgb: bool
    """
    source: int | str = 0
    width: int | None = None
    height: int | None = None
    fps: int | None = None
    convert_to_rgb: bool = True
