import time

import numpy as np

from src.app.configs.cameras import MockCameraConfig
from src.app.configs.cameras.mock import SourceConfig, VideoSourceConfig
from src.app.configs.cameras.mock import DirectorySourceConfig

from .sources import FrameSource, VideoFrameSource, DirectoryFrameSource


class MockCamera:
    """Моковый адаптер камеры."""

    def __init__(self, config: MockCameraConfig):
        """
        Инициализирует моковую камеру.

        :param config: Конфигцрация моковой камеры.
        :type config: MockCameraConfig
        """
        self.source: FrameSource = self._create_source(
            source_config=config.source,
            width=config.width,
            height=config.height,
        )
        self.fps = config.fps

        self._frame_interval = 1.0 / self.fps
        self._last_frame_time = None

    def open(self) -> None:
        """Инициализирует моковый источник видеопотока."""
        self.source.open()

    def read(self) -> np.ndarray:
        """
        Возвращает кадр из мокового источника кадров.
        Выполняет задержку перед считыванием кадра для имитации указанного FPS.

        :raises RuntimeError: При ошибке считывания кадра.
        :return: Моковый видеокадр в формате ``H x W x C``.
        :rtype: numpy.ndarray
        """
        now = time.time()
        if self._last_frame_time is not None:
            elapsed = now - self._last_frame_time
            if elapsed < self._frame_interval:
                time.sleep(self._frame_interval - elapsed)

        self._last_frame_time = time.time()

        frame = self.source.read()
        if frame is None:
            raise RuntimeError("No frame available")

        return frame

    def close(self) -> None:
        """Освобождает ресурсы источника."""
        self.source.close()

    def get_actual_properties(self) -> tuple[int, int, float]:
        """
        Возвращает параметры мокового видеопотока.

        :return: Ширина, высота и FPS.
        :rtype: tuple[int, int, float]
        """
        width, height = self.source.get_resolution()
        return width, height, self.fps

    def _create_source(
        self,
        source_config: SourceConfig,
        width: int | None = None,
        height: int | None = None,
    ) -> FrameSource:
        """
        Создаёт объект :class:`FrameSource` на основе переданной конфигурации источника.

        :param source_config: Конфигурация источника кадров.
        :type source_config: SourceConfig
        :param width: Целевая ширина кадров.
        :type width: int, optional
        :param height: Целевая высота кадров.
        :type height: int, optional
        :raises TypeError: При неверном типе конфигурации источника.
        :return: Инициализированный источник кадров.
        :rtype: FrameSource
        """
        if isinstance(source_config, DirectorySourceConfig):
            return DirectoryFrameSource(
                frames_dir=source_config.path,
                width=width,
                height=height,
                extensions=source_config.extensions,
            )
        elif isinstance(source_config, VideoSourceConfig):
            return VideoFrameSource(
                video_path=source_config.path,
                width=width,
                height=height,
            )
        else:
            raise TypeError(f"Unknown source config type: {type(source_config)}")
