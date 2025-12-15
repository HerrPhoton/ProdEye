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
        """
        Инициализация менеджера для работы с изображениями.

        :param images_dir: Путь/пути до директории с изображениями.
        :type images_dir: PathLike | Iterable[PathLike]
        :param image_ext: Расширения изображений.
        :type image_ext: Iterable[str], optional
        :param recursive: Искать ли метки в поддиректориях ``images_dir``.
        :type recursive: bool, optional
        :raises ValueError: Если указанная директория/директории в ``images_dir`` не найдена.
        """
        super().__init__(images_dir, image_ext, recursive)

    def validate_images(self) -> list[str]:
        """
        Проверяет целостность изображений в :attr:`images_dir`.

        :return: Список поврежденных изображений.
        :rtype: list[str]
        """
        corrupted: list[str] = []
        for image_path in self.iter_files():
            if not self._is_corrupted(image_path):
                corrupted.append(str(image_path))

        return corrupted

    def rename_images(self, new_name: str, start_idx: int = 0, zero_padding: int = 0) -> list[tuple[str, str]]:
        """
        Переименовывает изображения по паттерну ``new_name_{idx}``.

        :param new_name: Базовое имя для новых файлов (префикс).
        :type new_name: str
        :param start_idx: Начальный индекс.
        :type start_idx: int, optional
        :param zero_padding: Количество нулей для паддинга индекса.
        :type zero_padding: int, optional
        :return: Список переименованных изображений ``(старое название, новое название)``.
        :rtype: list[tuple[str, str]]
        """
        renamed: list[tuple[str, str]] = []
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

    def _is_corrupted(self, image_path: PathLike) -> bool:
        """
        Проверяет, является ли изображение поврежденным.

        :param image_path: Путь к изображению.
        :type image_path: PathLike
        :return: ``True``, если изображение валидно; ``False`` - иначе.
        :rtype: bool
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True

        except Exception:
            return False
