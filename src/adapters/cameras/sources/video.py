import cv2
import numpy as np

from src.utils import PathLike


class VideoFrameSource:
    """Источник кадров моковой камеры на основе видеофайла."""

    def __init__(
        self,
        video_path: PathLike,
        width: int | None = None,
        height: int | None = None,
    ):
        """
        Инициализирует источник кадров видеофайлом.

        :param video_path: Путь до мокового видеофайла.
        :type video_path: PathLike
        :param width: Целевая ширина кадра.
        :type width: int, optional
        :param height: Целевая высота кадра.
        :type height: int, optional
        """
        self.video_path = str(video_path)
        self.width = width
        self.height = height

        self._cap = None

    def open(self) -> None:
        """
        Инициализирует объекта захвата кадров :class:`cv2.VideoCapture` из видео.

        :raises ValueError: При ошибке открытия видеофайла.
        """
        self._cap = cv2.VideoCapture(self.video_path)
        if not self._cap.isOpened():
            raise ValueError(f"Failed to open video file: {self.video_path}")

    def read(self) -> np.ndarray:
        """
        Возвращает кадр из мокового видеофайла.

        :raises ValueError: Если объект захвата кадров :class:`cv2.VideoCapture` не инициализирован.
        :return: Моковый видеокадр в формате ``H x W x C``.
        :rtype: numpy.ndarray
        """
        if self._cap is None:
            raise ValueError("Video is not initialized. Call open() first.")

        ret, frame = self._cap.read()
        if not ret:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        orig_h, orig_w = frame.shape[:2]

        target_w = self.width if self.width is not None else orig_w
        target_h = self.height if self.height is not None else orig_h

        frame = cv2.resize(frame, (target_w, target_h))

        return frame

    def close(self) -> None:
        """Освобождает ресурсы источника."""
        self._cap.release()

    def get_resolution(self) -> tuple[int, int]:
        """
        Возвращает разрешение мокового видеопотока.

        :return: Ширина и высота.
        :rtype: tuple[int, int]
        """
        return self.width, self.height
