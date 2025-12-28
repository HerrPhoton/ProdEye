from typing import Any, Literal, TypeAlias
from dataclasses import field, dataclass
from collections.abc import Iterable

from src.utils import IMAGE_EXTENSIONS


@dataclass(frozen=True)
class DirectorySourceConfig:
    """Источник кадров из директории.

    :var path: Путь до директории с моковыми кадрами.
    :vartype path: str
    :var extensions: Список расширений моковых кадров.
    :vartype extensions: Iterable[str], optional
    """
    path: str
    extensions: Iterable[str] = IMAGE_EXTENSIONS
    type: Literal["dir"] = field(init=False, default="dir")


@dataclass(frozen=True)
class VideoSourceConfig:
    """Источник кадров из видеофайла.

    :var path: Путь до мокового видеофайла.
    :vartype path: str
    """
    path: str
    type: Literal["video"] = field(init=False, default="video")


SourceConfig: TypeAlias = DirectorySourceConfig | VideoSourceConfig


@dataclass(frozen=True)
class MockCameraConfig:
    """
    Параметры инициализации моковой камеры.

    :var source: Источник видеокадров.
    :vartype source: SourceConfig
    :var width: Ширина кадра.
    :vartype width: int
    :var height: Высота кадра.
    :vartype height: int
    :var fps: Частота кадров.
    :vartype fps: int
    """
    source: SourceConfig
    width: int
    height: int
    fps: int


def parse(raw: dict[str, Any]) -> MockCameraConfig:
    """
    Создает экземпляр конфига моковой камеры :class:`MockCameraConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфига.
    :type raw: dict[str, Any]
    :return: Экземпляр конфига, инициализированный параметрами из словаря.
    :rtype: MockCameraConfig
    """
    source_raw = raw.get("source", {})
    source_type = source_raw.get("type")

    match source_type:
        case "dir":
            source = DirectorySourceConfig(
                path=source_raw.get("path"),
                extensions=set(source_raw.get("extensions", IMAGE_EXTENSIONS)),
            )

        case "video":
            source = VideoSourceConfig(
                path=source_raw.get("path"),
            )

        case _:
            raise ValueError(f"Unknown mock camera source type: {source_type}")

    resolution = raw.get("resolution", {})
    return MockCameraConfig(
        source=source,
        width=resolution.get("width"),
        height=resolution.get("height"),
        fps=raw.get("fps"),
    )
