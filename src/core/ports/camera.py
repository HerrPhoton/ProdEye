from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class Camera(Protocol):
    """Контракт источника видеокадров."""

    def open(self) -> None:
        """Инициализирует источник видеопотока."""
        pass

    def read(self) -> np.ndarray:
        """
        Считывает один видеокадр.

        :return: Кадр в формате ``H x W x C``.
        :rtype: numpy.ndarray
        """
        pass

    def close(self) -> None:
        """Освобождает ресурсы источника."""
        pass

    def get_actual_properties(self) -> tuple[int, int, float]:
        """
        Возвращает фактические параметры видеопотока.

        :return: Ширина, высота и FPS.
        :rtype: tuple[int, int, float]
        """
        pass
