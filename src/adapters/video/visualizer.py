from collections.abc import Callable

import cv2
import numpy as np

from src.core.ports.camera import Camera


class CameraVisualizer:
    """Утилита визуализации видеопотока камеры."""

    def __init__(self, camera: Camera):
        """
        Инициализирует визуализацию видеопотока камеры.

        :param camera: Экземпляр камеры для визуализации кадров с её видеопотока.
        :type camera: Camera
        """
        self.camera = camera

    @staticmethod
    def visualize_frame(frame: np.ndarray, winname: str = "Frame") -> None:
        """
        Визуализирует переданный кадр в отдельном окне.

        :param frame: RGB-кадр для визуализации.
        :type frame: numpy.ndarray
        :param winname: Название окна с визуализацией.
        :type winname: str, optional
        """
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imshow(winname, frame)
        cv2.waitKey(1)

    def visualize_stream(
        self,
        winname: str = "Video stream",
        frame_transform: Callable[[np.ndarray], np.ndarray] | None = None,
    ) -> None:
        """
        Визуализирует подключенный видеопоток в отдельном окне.

        :param winname: Название окна с визуализацией.
        :type winname: str, optional
        :param frame_transform: Обработчик кадра, применяемый перед визуализацией.
        :type frame_transform: Callable[[numpy.ndarray], numpy.ndarray], optional
        """
        try:
            while True:
                frame = self.camera.read()
                if frame_transform is not None:
                    frame = frame_transform(frame)

                self.visualize_frame(frame, winname)

        except KeyboardInterrupt:
            pass

        finally:
            self.camera.close()
            cv2.destroyAllWindows()
