from pathlib import Path
from collections.abc import Iterable

from PIL import Image

from .path import PathHandler
from ...utils import IMAGE_EXTENSIONS, PathLike


class YOLOImageHandler(PathHandler):

    def __init__(
        self,
        images_dir: PathLike | Iterable[PathLike],
        image_ext: Iterable[str] = IMAGE_EXTENSIONS,
        recursive: bool = False,
    ):
        """Инициализация менеджера для работы с изображениями.

        :param PathLike | Iterable[PathLike] images_dir: Путь/пути до директории с изображениями
        :param Iterable[str] image_ext: Расширения изображений
        :param bool recursive: Искать ли метки в поддиректориях `images_dir`
        :raises ValueError: Если указанная директория/директории в `images_dir` не найдена
        """
        super().__init__(images_dir, image_ext, recursive)

    def validate_images(self) -> list[str]:
        """Проверяет целостность изображений в `self.images_dir`.

        :return list[str]: Список поврежденных изображений
        """
        corrupted = []
        for image_path in self.iter_files():
            if not self._is_corrupted(image_path):
                corrupted.append(str(image_path))

        return corrupted

    def _is_corrupted(self, image_path: str | Path) -> bool:
        """Проверяет, является ли изображение поврежденным

        :param str | Path image_path: Путь к изображению
        :return: True если изображение валидно, False иначе
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True

        except Exception:
            return False
