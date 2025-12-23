import time

import numpy as np

from src.app.configs.cameras import MockCameraConfig


class MockCamera:
    """Моковый адаптер камеры."""

    def __init__(self, config: MockCameraConfig):
        self.width = config.width
        self.height = config.height
        self.fps = config.fps

        self._frame_interval = 1.0 / self.fps
        self._last_frame_time = None

    def open(self) -> None:
        """Инициализирует моковый источник видеопотока."""
        self._last_frame_time = time.time()

    def read(self) -> np.ndarray:
        """
        Генерирует видеокадр, состоящий из шума.

        :return: Моковый видеокадр в формате ``H x W x C``.
        :rtype: numpy.ndarray
        """
        now = time.time()
        if self._last_frame_time is not None:
            elapsed = now - self._last_frame_time
            if elapsed < self._frame_interval:
                time.sleep(self._frame_interval - elapsed)

        self._last_frame_time = time.time()

        frame = np.random.randint(0, 256, (self.height, self.width, 3), dtype=np.uint8)
        return frame

    def close(self) -> None:
        """Освобождает ресурсы источника."""
        self._last_frame_time = None

    def get_actual_properties(self) -> tuple[int, int, float]:
        """
        Возвращает параметры мокового видеопотока.

        :return: Ширина, высота и FPS.
        :rtype: tuple[int, int, float]
        """
        return self.width, self.height, self.fps
