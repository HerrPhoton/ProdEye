from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True)
class OpenCVCameraConfig:
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
    :vartype convert_to_rgb: bool, optional
    """
    source: int | str = 0
    width: int | None = None
    height: int | None = None
    fps: int | None = None
    convert_to_rgb: bool = True


def parse(raw: dict[str, Any]) -> OpenCVCameraConfig:
    """
    Создает экземпляр конфига камеры :class:`OpenCVCameraConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфига.
    :type raw: dict[str, Any]
    :return: Экземпляр конфига, инициализированный параметрами из словаря.
    :rtype: OpenCVCameraConfig
    """
    resolution = raw.get("resolution", {})
    return OpenCVCameraConfig(
        source=raw.get("source", 0),
        width=resolution.get("width"),
        height=resolution.get("height"),
        fps=raw.get("fps"),
        convert_to_rgb=raw.get("convert_to_rgb", True),
    )
