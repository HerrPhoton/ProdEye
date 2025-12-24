from typing import Any
from dataclasses import dataclass
from collections.abc import Iterable

from src.utils import IMAGE_EXTENSIONS


@dataclass(frozen=True)
class MockCameraConfig:
    """
    Параметры инициализации моковой камеры.

    :var frames_dir: Путь до директории с моковыми кадрами.
    :vartype frames_dir: str
    :var width: Ширина кадра.
    :vartype width: int
    :var height: Высота кадра.
    :vartype height: int
    :var fps: Частота кадров.
    :vartype fps: int
    :var extensions: Список расширений моковых кадров.
    :vartype extensions: Iterable[str], optional
    """
    frames_dir: str
    width: int
    height: int
    fps: int
    extensions: Iterable[str] = IMAGE_EXTENSIONS


def parse(raw: dict[str, Any]) -> MockCameraConfig:
    """
    Создает экземпляр конфига моковой камеры :class:`MockCameraConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфига.
    :type raw: dict[str, Any]
    :return: Экземпляр конфига, инициализированный параметрами из словаря.
    :rtype: MockCameraConfig
    """
    resolution = raw.get("resolution", {})
    return MockCameraConfig(
        frames_dir=raw.get("frames_dir"),
        width=resolution.get("width"),
        height=resolution.get("height"),
        fps=raw.get("fps"),
        extensions=set(raw.get("extensions", IMAGE_EXTENSIONS))
    )
