from pathlib import Path

import cv2
import numpy as np
from natsort import natsorted

from src.utils import IMAGE_EXTENSIONS, PathLike, normalize_extensions


class DirectoryFrameSource:
    """Источник кадров моковой камеры на основе директории с кадрами."""

    def __init__(
        self,
        frames_dir: PathLike,
        width: int,
        height: int,
        extensions: set[str] = IMAGE_EXTENSIONS,
    ):
        """
        Инициализирует источник кадров изображениями из директории.

        :param frames_dir: Путь до директории с моковыми кадрами.
        :type frames_dir: PathLike
        :param width: Целевая ширина кадра.
        :type width: int | None
        :param height: Целевая высота кадра.
        :type height: int | None
        :param extensions: Список расширений моковых кадров.
        :type extensions: set[str], optional
        """
        self.frames_dir = Path(frames_dir)
        self.width = width
        self.height = height
        self.extensions = normalize_extensions(extensions)

        self._frames: list[Path] = []
        self._idx = 0

    def open(self) -> None:
        """
        Считывает моковые кадры из директории.
        Порядок кадров определяется естественной сортировкой (*natural sort*) имён файлов.

        :raises ValueError: Если моковые кадры не найдены в :attr:`frames_dir`.
        """
        frames: list[Path] = [
            file for file in self.frames_dir.iterdir()
            if file.suffix in self.extensions
        ]
        self._frames = natsorted(frames)

        if not self._frames:
            raise ValueError("No frames found")

    def read(self) -> np.ndarray | None:
        """
        Возвращает кадр из моковой директории :attr:`frames_dir`.
        Каждый вызов этой функции возвращает следующий по порядку кадр.

        :raises ValueError: Если список кадров :attr:`frames` пустой.
        :return: Моковый видеокадр в формате ``H x W x C``.
        :rtype: numpy.ndarray
        """
        if not self._frames:
            raise ValueError("Frames are not initialized. Call open() first.")

        if self._idx >= len(self._frames):
            self._idx = 0

        frame = cv2.imread(str(self._frames[self._idx]))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.width, self.height))

        self._idx += 1
        return frame

    def close(self) -> None:
        """Освобождает ресурсы источника."""
        self._frames.clear()
        self._idx = 0

    def get_resolution(self) -> tuple[int, int]:
        """
        Возвращает разрешение мокового видеопотока.

        :return: Ширина и высота.
        :rtype: tuple[int, int]
        """
        return self.width, self.height
