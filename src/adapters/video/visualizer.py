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

    def visualize_stream(self, winname: str = "Video stream") -> None:
        """
        Визуализирует подключенный видеопоток в отдельном окне.

        :param winname: Название окна с визуализацией.
        :type winname: str, optional
        """
        while True:
            try:
                frame = self.camera.read()
                self.visualize_frame(frame, winname)
            except KeyboardInterrupt:
                break

        self.camera.close()
