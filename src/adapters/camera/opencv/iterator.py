from collections.abc import Iterator

import numpy as np

from .camera import OpenCVCamera


class OpenCVCameraIterator(Iterator[np.ndarray]):
    """Итератор по видеокадрам камеры."""

    def __init__(self, camera: OpenCVCamera):
        self.camera = camera

    def __iter__(self):
        return self

    def __next__(self) -> np.ndarray:
        return self.camera.read()
