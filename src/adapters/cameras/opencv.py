import contextlib

import cv2
import numpy as np

from src.core.ports import CameraProperties
from src.exceptions import CameraOpenError, CameraReadError
from src.app.configs.cameras import OpenCVCameraConfig


class OpenCVCamera:
    """Адаптер камеры на базе OpenCV."""

    def __init__(self, config: OpenCVCameraConfig):
        """
        Инициализирует камеру на базе OpenCV.

        :param config: Конфигурация камеры OpenCV.
        :type config: OpenCVCameraConfig
        """
        self.source = config.source
        self.width = config.width
        self.height = config.height
        self.fps = config.fps
        self.convert_to_rgb = config.convert_to_rgb

        self._cap: cv2.VideoCapture | None = None
        self._is_open: bool = False

    def open(self) -> None:
        """
        Выполняет подключение к источнику видео.
        Если указаны параметры :attr:`width`, :attr:`height` или :attr:`fps`,
        то драйвер выбирает ближайшее поддерживаемое разрешение и FPS.

        :raises CameraOpenError: При ошибке подключения к источнику видео.
        """
        if self._is_open:
            return

        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            cap.release()
            raise CameraOpenError(f"The video source could not be opened: {self.source}")

        if self.width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.width))

        if self.height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.height))

        if self.fps is not None:
            cap.set(cv2.CAP_PROP_FPS, float(self.fps))

        self._cap = cap
        self._is_open = True

    def close(self) -> None:
        """Выполняет отключение от источника видео."""
        if self._cap is not None:
            with contextlib.suppress(Exception):
                self._cap.release()

        self._cap = None
        self._is_open = False

    def read(self) -> np.ndarray:
        """
        Считывает кадр с видеопотока.

        :raises CameraReadError: При ошибке считывания кадра.
        :return: Полученный кадр.
        :rtype: numpy.ndarray
        """
        if not self._is_open:
            self.open()

        ok, frame = self._cap.read()
        if not ok:
            raise CameraReadError("Couldn't read frame from source")

        if self.convert_to_rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return frame

    def get_actual_properties(self) -> CameraProperties:
        """
        Возвращает текущие параметры источника видео.

        :return: Ширина, высота и FPS.
        :rtype: CameraProperties
        """
        if not self._is_open:
            self.open()

        width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = float(self._cap.get(cv2.CAP_PROP_FPS) or 0.0)

        return CameraProperties(
            width=width,
            height=height,
            fps=fps
        )
