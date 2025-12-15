from typing import NamedTuple
from pathlib import Path
from collections.abc import Iterable, Generator

from ...utils import IMAGE_EXTENSIONS, LABEL_EXTENSIONS, PathLike, normalize_to_paths
from ..structures import Split, YOLODataset


class RenamedSample(NamedTuple):
    image: tuple[str, str]  # (старый путь изображения, новый путь изображения)
    label: tuple[str, str]  # (старый путь метки, новый путь метки)


class YOLOSampleHandler:

    def __init__(
        self,
        images_dir: PathLike | Iterable[PathLike],
        labels_dir: PathLike | Iterable[PathLike],
        image_ext: Iterable[str] = IMAGE_EXTENSIONS,
        labels_ext: Iterable[str] = LABEL_EXTENSIONS,
    ):
        """
        Инициализация менеджера для работы с сэмплами (парами изображение-метка).

        :param images_dir: Путь/пути до директории с изображениями.
        :type images_dir: PathLike | Iterable[PathLike]
        :param labels_dir: Путь/пути до директории с метками.
        :type labels_dir: PathLike | Iterable[PathLike]
        :param image_ext: Расширения изображений.
        :type image_ext: Iterable[str], optional
        :param labels_ext: Расширения файлов с метками.
        :type labels_ext: Iterable[str], optional
        :raises ValueError: Если указанная директория/директории в ``images_dir`` или ``labels_dir`` не найдены.
        """
        images_dirs = normalize_to_paths(images_dir)
        labels_dirs = normalize_to_paths(labels_dir)

        self.splits: list[Split] = []
        for images_dir, labels_dir in zip(images_dirs, labels_dirs):
            self.splits.append(Split(
                images_dir=images_dir,
                labels_dir=labels_dir,
                image_ext=image_ext,
                labels_ext=labels_ext
            ))

    @classmethod
    def from_dataset(cls, dataset: YOLODataset) -> 'YOLOSampleHandler':
        """
        Создает экземпляр :class:`YOLOSampleHandler` с директориями из ``dataset``.

        :param dataset: Экземпляр датасета :class:`YOLODataset`.
        :type dataset: YOLODataset
        :return: Экземпляр :class:`YOLOSampleHandler` с изображениями и метками из ``dataset``.
        :rtype: YOLOSampleHandler
        """
        handler = cls.__new__(cls)
        handler.splits = list(dataset.splits.values())
        return handler

    def create_empty_labels(self, skip_existing: bool = True) -> list[str]:
        """
        Создает файлы с пустыми метками для каждого изображения.

        :param skip_existing: Пропускать ли файлы с уже существующими метками.
        :type skip_existing: bool, optional
        :raises ValueError: Если не удалось сформировать путь до метки изображения.
        :return: Пути к созданным меткам.
        :rtype: list[str]
        """
        created: list[str] = []
        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if label_path.exists() and skip_existing:
                continue

            label_path.touch()
            created.append(str(label_path))

        return created

    def get_unlabeled_images(self) -> list[str]:
        """
        Возвращает список изображений без меток.

        :raises ValueError: Если не удалось сформировать путь до метки изображения.
        :return: Список путей до изображений без метки.
        :rtype: list[str]
        """
        unlabeled: list[str] = []
        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if not label_path.exists():
                unlabeled.append(str(image_path))

        return unlabeled

    def remove_unlabeled_images(self) -> list[str]:
        """
        Удаляет изображения без меток.

        :raises ValueError: Если не удалось сформировать путь до метки изображения.
        :return: Список путей удаленных файлов.
        :rtype: list[str]
        """
        removed: list[str] = []
        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if not label_path.exists():
                removed.append(str(image_path))
                image_path.unlink()

        return removed

    def rename_samples(self, new_name: str, start_idx: int = 0, zero_padding: int = 0) -> list[RenamedSample]:
        """
        Переименовывает сэмплы по паттерну ``new_name_{idx}``.

        :param new_name: Базовое имя для новых файлов (префикс).
        :type new_name: str
        :param start_idx: Начальный индекс.
        :type start_idx: int, optional
        :param zero_padding: Количество нулей для паддинга индекса.
        :type zero_padding: int, optional
        :return: Список переименованных сэмплов.
        :rtype: list[RenamedSample]
        """
        renamed = []
        idx = start_idx

        for image_path, label_path in self._iter_samples():
            # Паддинг индекса
            idx_str = str(idx).zfill(zero_padding)

            # Новое имя для изображения
            new_image_name = f"{new_name}_{idx_str}{image_path.suffix}"
            new_image_path = image_path.parent / new_image_name

            # Новое имя для метки
            new_label_name = f"{new_name}_{idx_str}{label_path.suffix}"
            new_label_path = label_path.parent / new_label_name

            # Переименовываем файлы
            image_path.rename(new_image_path)
            label_path.rename(new_label_path)

            renamed.append(RenamedSample(
                image=(str(image_path), str(new_image_path)),
                label=(str(label_path), str(new_label_path))
            ))
            idx += 1

        return renamed

    def _get_label_path(self, image_path: Path) -> Path:
            """
            Возвращает путь к метке для указанного изображения.

            :param image_path: Путь к изображению.
            :type image_path: pathlib.Path
            :raises ValueError: Если не удалось сформировать путь до метки изображения.
            :return: Путь до метки.
            :rtype: pathlib.Path
            """
            for split in self.splits:
                try:
                    return split.get_label_path(image_path)
                except ValueError:
                    continue
            raise ValueError(f"Не удалось найти метку для изображения {image_path}")

    def _iter_images(self) -> Generator[Path, None, None]:
        """
        Итерируется по изображениям во всех сплитах.

        :return: Генератор путей к изображениям.
        :rtype: Generator[pathlib.Path, None, None]
        """
        for split in self.splits:
            yield from split.iter_images()

    def _iter_labels(self) -> Generator[Path, None, None]:
        """
        Итерируется по меткам во всех сплитах.

        :return: Генератор путей к меткам.
        :rtype: Generator[pathlib.Path, None, None]
        """
        for split in self.splits:
            yield from split.iter_labels()

    def _iter_samples(self) -> Generator[tuple[Path, Path], None, None]:
        """
        Итерируется по парам изображение-метка (если оба существуют) по всем сплитам.

        :return: Генератор путей к сэмплам (путь до изображения, путь до метки).
        :rtype: Generator[tuple[pathlib.Path, pathlib.Path], None, None]
        """
        for split in self.splits:
            yield from split.iter_samples()
