from pathlib import Path
from dataclasses import dataclass
from collections.abc import Iterable, Generator

from ...utils import IMAGE_EXTENSIONS, LABEL_EXTENSIONS, PathLike


@dataclass
class Split:
    images_dir: PathLike
    labels_dir: PathLike
    image_ext: Iterable[str] = IMAGE_EXTENSIONS
    labels_ext: Iterable[str] = LABEL_EXTENSIONS

    def __post_init__(self):
        """Инициализация менеджеров путей после создания объекта."""
        from ..handlers import PathHandler

        self.images_dir = Path(self.images_dir).resolve()
        self.labels_dir = Path(self.labels_dir).resolve()

        self._image_manager = PathHandler(
            self.images_dir,
            self.image_ext,
        )
        self._label_manager = PathHandler(
            self.labels_dir,
            self.labels_ext,
        )

    @classmethod
    def from_dir(
        cls,
        split_path: PathLike,
        image_ext: Iterable[str] = IMAGE_EXTENSIONS,
        labels_ext: Iterable[str] = LABEL_EXTENSIONS,
    ) -> 'Split':
        """Создает экземпляр Split на основе переданного пути до директории сплита.
        Ожидается, что директория и изображениями находится по пути `split_path/images/`,
        а директория с метками находится по пути `split_path/labels/`.

        :param PathLike split_path: Путь до директории сплита
        :param Iterable[str] image_ext: Расширения изображений
        :param Iterable[str] labels_ext: Расширения меток
        :return Split: Инициализированный экземпляр Split
        """
        split_path = Path(split_path)
        return cls(
            images_dir=split_path / "images",
            labels_dir=split_path / "labels",
            image_ext=image_ext,
            labels_ext=labels_ext,
        )

    def iter_images(self) -> Generator[Path, None, None]:
        """Итерируется по изображениям в сплите.

        :yield Generator[Path, None, None]: Путь до изображения
        """
        yield from self._image_manager.iter_files()

    def iter_labels(self) -> Generator[Path, None, None]:
        """Итерируется по меткам в сплите.

        :yield Generator[Path, None, None]: Путь до метки
        """
        yield from self._label_manager.iter_files()

    def iter_samples(self) -> Generator[tuple[Path, Path], None, None]:
        """Итерируется по парам изображение-метка (если оба существуют).

        :yield Generator[tuple[Path, Path], None, None]: путь до изображения, путь до метки
        """
        for image_path in self.iter_images():
            label_path = self._get_label_path(image_path)
            if label_path.exists():
                yield image_path, label_path

    def exists(self) -> bool:
        """Проверяет существование директорий сплита.

        :return bool: True, если директории `self.images_dir` и `self.labels_dir` существуют;
                      False - иначе
        """
        return self.images_dir.exists() and self.labels_dir.exists()

    def count_images(self) -> int:
        """Возвращает количество изображений в сплите.

        :return int: Количество изображений
        """
        return sum(1 for _ in self.iter_images())

    def count_labels(self) -> int:
        """Возвращает количество меток в сплите.

        :return int: Количество меток
        """
        return sum(1 for _ in self.iter_labels())

    def count_samples(self) -> int:
        """Возвращает количество пар изображение-метка в сплите.

        :return int: Количество пар изображение-метка
        """
        return sum(1 for _ in self.iter_samples())

    def _get_label_path(self, image_path: Path) -> Path:
        """Возвращает путь к метке для указанного изображения.

        :param Path image_path: Путь до изображения
        :return Path: Путь до метки
        """
        rel = image_path.relative_to(self.images_dir)
        return self.labels_dir / rel.with_suffix(".txt")
