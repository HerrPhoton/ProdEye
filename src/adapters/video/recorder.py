import time
from pathlib import Path

import cv2
import numpy as np

from src.utils import PathLike
from src.exceptions import FrameSaveError
from src.core.ports.camera import Camera


class FrameRecorder:
    """Утилита для сохранения кадров из видеопотока камеры."""

    def __init__(self, camera: Camera):
        """
        Инициализирует утилиту сохранения кадров.

        :param camera: Экземпляр камеры для сохранения кадров с её видеопотока.
        :type camera: Camera
        """
        self.camera = camera

    @staticmethod
    def save_frame(frame: np.ndarray, frame_path: PathLike) -> str:
        """
        Сохраняет кадр по указанному пути.

        :param frame: RGB-кадр для сохранения.
        :type frame: numpy.ndarray
        :param frame_path: Путь к файлу для сохранения.
        :type frame_path: PathLike
        :raises FrameSaveError: При ошибке сохранения кадра.
        :return: Абсолютный путь к сохраненному кадру.
        :rtype: str
        """
        frame_path = Path(frame_path).resolve()
        frame_path.parent.mkdir(parents=True, exist_ok=True)

        frame_to_save = frame.copy()
        frame_to_save = cv2.cvtColor(frame_to_save, cv2.COLOR_BGR2RGB)
        frame_path = str(frame_path)

        success = cv2.imwrite(frame_path, frame_to_save)
        if not success:
            raise FrameSaveError(f"Failed to save frame on path: {frame_path}")

        return frame_path

    def save_stream(
        self,
        save_path: PathLike,
        interval: float = 0.0,
        filename_prefix: str = "frame"
    ) -> list[str]:
        """
        Сохраняет кадры из видеопотока с указанным интервалом времени в формате
        ``filename_prefix_000001.jpg``.

        :param save_path: Путь к директории для сохранения кадров.
        :type save_path: PathLike
        :param interval: Интервал времени между сохранениями кадров (в секундах).
        :type interval: float, optional
        :param filename_prefix: Префикс для имен файлов с сохраненными кадрами.
        :type filename_prefix: str, optional
        :raises FrameSaveError: При ошибке сохранения кадра.
        :return: Абсолютные пути до сохраненных кадров.
        :rtype: list[str]
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        last_save_time = 0.0
        frame_count = 0

        saved_frames: list[str] = []
        while True:
            try:
                current_time = time.time()

                # Проверка, прошло ли достаточно времени с последнего сохранения
                if current_time - last_save_time >= interval:
                    frame = self.camera.read()

                    filename = f"{filename_prefix}_{frame_count:06d}.jpg"
                    frame_path = self.save_frame(frame, save_path / filename)
                    saved_frames.append(frame_path)

                    last_save_time = current_time
                    frame_count += 1

            except KeyboardInterrupt:
                break

        self.camera.close()
        return saved_frames
