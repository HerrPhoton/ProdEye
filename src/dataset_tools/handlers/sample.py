from typing import NamedTuple
from pathlib import Path
from collections.abc import Iterable, Generator

from src.utils import IMAGE_EXTENSIONS, LABEL_EXTENSIONS, PathLike, normalize_to_paths

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
        """Инициализация менеджера для работы с сэмплами (парами изображение-метка).

        :param PathLike | Iterable[PathLike] images_dir: Путь/пути до директории с изображениями
        :param PathLike | Iterable[PathLike] labels_dir: Путь/пути до директории с метками
        :param Iterable[str] image_ext: Расширения изображений
        :param Iterable[str] labels_ext: Расширения файлов с метками
        :raises ValueError: Если указанная директория/директории в `images_dir` или `labels_dir` не найдены
        """
        images_dirs = normalize_to_paths(images_dir)
        labels_dirs = normalize_to_paths(labels_dir)

        self.splits: list[Split] = []
        for images_dir, labels_dir in zip(images_dirs, labels_dirs):
            self.splits.append(Split(
                name="",
                images_dir=images_dir,
                labels_dir=labels_dir,
                image_ext=image_ext,
                labels_ext=labels_ext
            ))

    @classmethod
    def from_dataset(cls, dataset: YOLODataset) -> 'YOLOSampleHandler':
        """Создает экземпляр YOLOSampleHandler с директориями из `dataset`.

        :param YOLODataset dataset: Экземпляр YOLODataset
        :return YOLOSampleHandler: Экземпляр YOLOSampleHandler с изображениями и метками из `dataset`
        """
        handler = cls.__new__(cls)
        handler.splits = list(dataset.splits.values())
        return handler

    def create_empty_labels(self, skip_existing: bool = True) -> list[str]:
        """Создает файлы с пустыми метками для каждого изображения.

        :param bool skip_existing: Пропускать ли файлы с уже существующими метками
        :raises ValueError: Если не удалось сформировать путь до метки изображения
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
        """Возвращает список изображений без меток.

        :raises ValueError: Если не удалось сформировать путь до метки изображения
        :return list[str]: Список путей до изображений без метки
        """
        unlabeled = []
        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if not label_path.exists():
                unlabeled.append(str(image_path))

        return unlabeled

    def remove_unlabeled_images(self) -> list[str]:
        """Удаляет изображения без меток.

        :raises ValueError: Если не удалось сформировать путь до метки изображения
        :return list[str]: Список удаленных файлов
        """
        removed = []
        for image_path in self._iter_images():
            label_path = self._get_label_path(image_path)

            if not label_path.exists():
                removed.append(str(image_path))
                image_path.unlink()

        return removed

    def rename_samples(self, new_name: str, start_idx: int = 0, zero_padding: int = 0) -> list[RenamedSample]:
        """Переименовывает сэмплы по паттерну `new_name_{idx}`.

        :param str new_name: Базовое имя для новых файлов
        :param int start_idx: Начальный индекс
         :param int zero_padding: Количество нулей для паддинга индекса
        :return list[RenamedSample]: Список переименованных сэмплов
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
            """Возвращает путь к метке для указанного изображения.

            :raises ValueError: Если не удалось сформировать путь до метки изображения
            :return Path: Путь до метки для изображения
            """
            for split in self.splits:
                try:
                    return split._get_label_path(image_path)
                except ValueError:
                    continue
            raise ValueError(f"Не удалось найти метку для изображения {image_path}")

    def _iter_images(self) -> Generator[Path, None, None]:
        """Итерируется по изображениям во всех сплитах.

        :yield Generator[Path, None, None]: Путь до изображения
        """
        for split in self.splits:
            yield from split.iter_images()

    def _iter_labels(self) -> Generator[Path, None, None]:
        """Итерируется по меткам во всех сплитах.

        :yield Generator[Path, None, None]: Путь до метки
        """
        for split in self.splits:
            yield from split.iter_labels()

    def _iter_samples(self) -> Generator[tuple[Path, Path], None, None]:
        """Итерируется по парам изображение-метка (если оба существуют) по всем сплитам.

        :yield Generator[tuple[Path, Path], None, None]: путь до изображения, путь до метки
        """
        for split in self.splits:
            yield from split.iter_samples()
