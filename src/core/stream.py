import contextlib
from collections.abc import Iterable, Iterator

import cv2
import numpy as np

from configs.camera import CameraConfig

from .exceptions import CameraOpenError, CameraReadError


class VideoStream(Iterable[np.ndarray]):

    def __init__(self, config: CameraConfig | None = None):
        self.config = config or CameraConfig()
        self._cap: cv2.VideoCapture | None = None
        self._is_open: bool = False

    def open(self) -> None:
        """Выполняет подключение к источнику видео

        :raises CameraOpenError: При ошибке подключения к источнику видео
        """
        if self._is_open:
            return

        source = self.config.source
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            cap.release()
            raise CameraOpenError(f"Не удалось открыть источник видео: {source}")

        if self.config.width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.config.width))

        if self.config.height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.config.height))

        if self.config.fps is not None:
            cap.set(cv2.CAP_PROP_FPS, float(self.config.fps))

        self._cap = cap
        self._is_open = True

    def close(self) -> None:
        """Выполняет отключение от источника видео"""

        if self._cap is not None:
            with contextlib.suppress(Exception):
                self._cap.release()

        self._cap = None
        self._is_open = False

    def read(self) -> np.ndarray:
        """Считывает кадр с видеопотока

        :raises CameraReadError: При ошибке считывания кадра
        :return np.ndarray: Полученный кадр
        """
        if not self._is_open:
            self.open()

        ok, frame = self._cap.read()
        if not ok:
            raise CameraReadError("Не удалось прочитать кадр из источника")

        if self.config.convert_to_rgb:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return frame

    def get_actual_properties(self) -> tuple[int, int, float]:
        """Возвращает текущие параметры источника видео

        :return tuple[int, int, float]: Ширина, высота и FPS
        """
        if not self._is_open:
            self.open()

        width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = float(self._cap.get(cv2.CAP_PROP_FPS) or 0.0)

        return width, height, fps

    def visualize_frame(self, frame: np.ndarray) -> None:
        """Визуализирует переданный кадр в отдельном окне

        :param np.ndarray frame: Кадр для визуализации
        """
        if not self._is_open:
            self.open()

        cv2.imshow("Frame", frame)

    def visualize_stream(self) -> None:
        """Визуализирует подключенный видеопоток"""
        if not self._is_open:
            self.open()

        while True:
            try:
                frame = self.read()
                cv2.imshow("Video stream", frame)
                cv2.waitKey(1)
            except KeyboardInterrupt:
                break

    def __enter__(self) -> "VideoStream":
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __iter__(self) -> Iterator[np.ndarray]:
        if not self._is_open:
            self.open()

        while True:
            frame = self.read()
            yield frame
