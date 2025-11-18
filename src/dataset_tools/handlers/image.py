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

    def rename_images(self, new_name: str, start_idx: int = 0, zero_padding: int = 0) -> list[tuple[str, str]]:
        """Переименовывает изображения по паттерну `new_name_{idx}`.

        :param str new_name: Базовое имя для новых файлов
        :param int start_idx: Начальный индекс
        :param int zero_padding: Количество нулей для паддинга индекса
        :return list[tuple[str, str]]: Список переименованных изображений (старое название, новое название)
        """
        renamed = []
        idx = start_idx

        for image_path in self.iter_files():
            # Паддинг индекса
            idx_str = str(idx).zfill(zero_padding)

            # Новое имя для изображения
            new_image_name = f"{new_name}_{idx_str}{image_path.suffix}"
            new_image_path = image_path.parent / new_image_name

            # Переименовываем изображение
            image_path.rename(new_image_path)

            renamed.append((str(image_path), str(new_image_path)))
            idx += 1

        return renamed

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
