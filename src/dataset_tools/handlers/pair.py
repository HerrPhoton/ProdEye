from pathlib import Path
from collections.abc import Iterable

import yaml

from src.utils import IMAGE_EXTENSIONS, LABEL_EXTENSIONS, PathLike

from .path import PathHandler
from ..structures import Split


class YOLOPairHandler:

    def __init__(
        self,
        images_dir: PathLike | Iterable[PathLike],
        labels_dir: PathLike | Iterable[PathLike],
        image_ext: Iterable[str] = IMAGE_EXTENSIONS,
        labels_ext: Iterable[str] = LABEL_EXTENSIONS,
    ):
        """Инициализация менеджера для работы с парами изображение-метка.

        :param PathLike | Iterable[PathLike] images_dir: Путь/пути до директории с изображениями
        :param PathLike | Iterable[PathLike] labels_dir: Путь/пути до директории с метками
        :param Iterable[str] image_ext: Расширения изображений
        :param Iterable[str] labels_ext: Расширения файлов с метками
        :raises ValueError: Если указанная директория/директории в `images_dir` или `labels_dir` не найдены
        """
        self._image_manager = PathHandler(images_dir, image_ext)
        self._label_manager = PathHandler(labels_dir, labels_ext)

    @classmethod
    def from_splits(cls, splits: Iterable[Split]) -> 'YOLOPairHandler':
        """Создает экземпляр YOLOPairHandler с директориями из сплитов.

        :param Iterable[Split] splits: Экземпляры сплитов
        :return YOLOPairHandler: Экземпляр YOLOPairHandler с изображениями и метками из сплитов
        """
        image_paths = []
        label_paths = []

        for split in splits:
            image_paths.append(split.images_dir)
            label_paths.append(split.labels_dir)

        return cls(
            images_dir=image_paths,
            labels_dir=label_paths
        )

    @classmethod
    def from_yaml(cls, data_yaml: PathLike) -> 'YOLOPairHandler':
        """Создает экземпляр YOLOPairHandler с директориями из `data_yaml`.

        :param PathLike data_yaml: Путь к data.yaml
        :return YOLOPairHandler: Экземпляр YOLOPairHandler с изображениями и метками из `data_yaml`
        """
        data_yaml = Path(data_yaml)

        with open(data_yaml) as file:
            data = yaml.safe_load(file)

        image_paths = []
        label_paths = []

        for split in ["train", "val", "test"]:
            if split in data:
                path = Path(data[split])

                if not path.is_absolute():
                    path = data_yaml.parent / path

                image_path = path.resolve()
                image_paths.append(image_path)

                label_path = Path(str(image_path).replace("images", "labels"))
                label_paths.append(label_path)

        return cls(
            images_dir=image_paths,
            labels_dir=label_paths
        )

    def create_empty_labels(self, skip_existing: bool = True) -> list[str]:
        """Создает файлы с пустыми метками в `self.labels_dir` для каждого изображения из
        `self.images_dir`.

        :param bool skip_existing: Пропускать ли файлы с уже существующими метками
        :return list[str]: Пути к созданным меткам
        """
        created = []

        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if label_path.exists() and skip_existing:
                continue

            label_path.touch()
            created.append(str(label_path))

        return created

    def get_unlabeled_images(self) -> list[str]:
        """Возвращает список изображений без меток в `self.images_dir`.

        :param list[str]: Список имен файлов изображений без меток
        """
        unlabeled = []
        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if not label_path.exists():
                unlabeled.append(str(image_path))

        return unlabeled

    def remove_unlabeled_images(self) -> list[str]:
        """Удаляет изображения без меток.

        :return list[str]: Список удаленных файлов
        """
        removed = []
        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if not label_path.exists():
                removed.append(str(image_path))
                image_path.unlink()

        return removed
