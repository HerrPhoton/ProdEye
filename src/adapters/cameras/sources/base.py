from typing import Protocol

import numpy as np


class FrameSource(Protocol):
    """Источник кадров моковой камеры."""

    def open(self) -> None:
        """Инициализирует моковый источник видеопотока."""
        pass

    def read(self) -> np.ndarray:
        """
        Возвращает кадр из мокового источника кадров.

        :return: Моковый видеокадр в формате ``H x W x C``.
        :rtype: numpy.ndarray
        """
        pass

    def close(self) -> None:
        """Освобождает ресурсы источника."""
        pass

    def get_resolution(self) -> None:
        """
        Возвращает разрешение мокового видеопотока.

        :return: Ширина и высота.
        :rtype: tuple[int, int]
        """
        pass
