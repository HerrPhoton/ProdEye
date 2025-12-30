from typing import Protocol, runtime_checkable

import numpy as np

from src.core.dto import Detection


@runtime_checkable
class Detector(Protocol):
    """Контракт детектора объектов."""

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Выполняет детекцию объектов на кадре.

        :param frame: Видеокадр.
        :type frame: numpy.ndarray
        :return: Список детекций на видеокадре.
        :rtype: list[Detection]
        """
        pass
