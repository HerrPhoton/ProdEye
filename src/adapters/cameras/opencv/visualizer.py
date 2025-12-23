import cv2
import numpy as np

from .camera import OpenCVCamera


class OpenCVVisualizer:
    """Утилита визуализации видеопотока через OpenCV."""

    def __init__(self, camera: OpenCVCamera):
        """Инициализрует утилиту для визуализации кадров с камеры :class:`OpenCVCamera`.

        :param camera: Экземпляр камеры для визуализации кадров с её видеопотока.
        :type camera: OpenCVCamera
        """
        self.camera = camera

    @staticmethod
    def visualize_frame(frame: np.ndarray, winname: str = "Frame") -> None:
        """
        Визуализирует переданный кадр в отдельном окне.

        :param frame: Кадр для визуализации.
        :type frame: numpy.ndarray
        :param winname: Название окна с визуализацией.
        :type winname: str, optional
        """
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
                if self.camera.convert_to_rgb:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                self.visualize_frame(frame, winname)
            except KeyboardInterrupt:
                break

        self.camera.close()
