import time
from pathlib import Path

import cv2
import numpy as np

from src.utils import normalize_extensions
from src.app.configs.cameras import MockCameraConfig


class MockCamera:
    """Моковый адаптер камеры."""

    def __init__(self, config: MockCameraConfig):
        self.frames_dir = Path(config.frames_dir)
        self.width = config.width
        self.height = config.height
        self.fps = config.fps
        self.extensions = normalize_extensions(config.extensions)

        self._frames: list[Path] = []
        self._idx = 0
        self._frame_interval = 1.0 / self.fps
        self._last_frame_time = None

    def open(self) -> None:
        """Инициализирует моковый источник видеопотока.

        :raises ValueError: Если моковые кадры не найдены в :attr:`frames_dir`.
        """
        frames: list[Path] = [
            file for file in self.frames_dir.iterdir()
            if file.suffix in self.extensions
        ]
        self.frames = sorted(frames)

        if not self.frames:
            raise ValueError("No frames found")

    def read(self) -> np.ndarray:
        """
        Возвращает кадр из моковой директории :attr:`frames_dir`.
        Каждый вызов этой функции возвращает следующий по порядку кадр.

        :return: Моковый видеокадр в формате ``H x W x C``.
        :rtype: numpy.ndarray
        """
        if not self.frames:
            return

        if self._idx >= len(self.frames):
            self._idx = 0

        now = time.time()
        if self._last_frame_time is not None:
            elapsed = now - self._last_frame_time
            if elapsed < self._frame_interval:
                time.sleep(self._frame_interval - elapsed)

        self._last_frame_time = time.time()

        frame = cv2.imread(str(self.frames[self._idx]))
        frame = cv2.resize(frame, (self.width, self.height))

        self._idx += 1
        return frame

    def close(self) -> None:
        """Освобождает ресурсы источника."""
        self._frames.clear()
        self._idx = 0
        self._last_frame_time = None

    def get_actual_properties(self) -> tuple[int, int, float]:
        """
        Возвращает параметры мокового видеопотока.

        :return: Ширина, высота и FPS.
        :rtype: tuple[int, int, float]
        """
        return self.width, self.height, self.fps
