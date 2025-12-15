from pathlib import Path
from dataclasses import dataclass
from collections.abc import Iterable, Generator

import fiftyone as fo

from .label import YOLOLabel
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

        self._image_handler = PathHandler(
            self.images_dir,
            self.image_ext,
        )
        self._label_handler = PathHandler(
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
        """
        Создает экземпляр :class:`Split` на основе переданного пути до директории сплита.

        Ожидается, что директория и изображениями находится по пути ``split_path/images/``,
        а директория с метками находится по пути ``split_path/labels/``.

        :param split_path: Путь до директории сплита.
        :type split_path: PathLike
        :param image_ext: Расширения изображений.
        :type image_ext: Iterable[str], optional
        :param labels_ext: Расширения меток
        :type labels_ext: Iterable[str], optional
        :return: Инициализированный экземпляр :class:`Split`.
        :rtype: Split
        """
        split_path = Path(split_path)
        return cls(
            images_dir=split_path / "images",
            labels_dir=split_path / "labels",
            image_ext=image_ext,
            labels_ext=labels_ext,
        )

    def iter_images(self) -> Generator[Path, None, None]:
        """
        Итерируется по изображениям в сплите.

        :return: Генератор путей до изображений.
        :rtype: Generator[pathlib.Path, None, None]
        """
        yield from self._image_handler.iter_files()

    def iter_labels(self) -> Generator[Path, None, None]:
        """
        Итерируется по меткам в сплите.

        :return: Генератор путей до меток.
        :rtype: Generator[pathlib.Path, None, None]
        """
        yield from self._label_handler.iter_files()

    def iter_samples(self) -> Generator[tuple[Path, Path], None, None]:
        """
        Итерируется по парам изображение-метка (если оба существуют).

        :return: Генератор путей до сэмплов (путь до изображения, путь до метки).
        :rtype: Generator[tuple[pathlib.Path, pathlib.Path], None, None]
        """
        for image_path in self.iter_images():
            label_path = self.get_label_path(image_path)
            if label_path.exists():
                yield image_path, label_path

    def exists(self) -> bool:
        """
        Проверяет существование директорий сплита.

        :return: ``True``, если директории ``self.images_dir`` и ``self.labels_dir`` существуют;
            ``False`` - иначе.
        :rtype: bool
        """
        return self.images_dir.exists() and self.labels_dir.exists()

    def count_images(self) -> int:
        """
        Возвращает количество изображений в сплите.

        :return: Количество изображений.
        :rtype: int
        """
        return sum(1 for _ in self.iter_images())

    def count_labels(self) -> int:
        """
        Возвращает количество меток в сплите.

        :return: Количество меток.
        :rtype: int
        """
        return sum(1 for _ in self.iter_labels())

    def count_samples(self) -> int:
        """
        Возвращает количество пар изображение-метка в сплите.

        :return: Количество сэмплов.
        :rtype: int
        """
        return sum(1 for _ in self.iter_samples())

    def get_fiftyone_samples(self) -> list[fo.Sample]:
        """
        Возвращает сэмплы сплита в формате FiftyOne (:class:`fiftyone.Sample`).

        :return: Список сэмплов сплита в виде экземпляров :class:`fiftyone.Sample`.
        :rtype: list[fiftyone.Sample]
        """
        # Формирование списка сэмплов в формате FiftyOne
        samples: list[fo.Sample] = []
        for image_path, label_path in self.iter_samples():
            label = YOLOLabel(label_path)

            detections = [
                fo.Detection(
                    label=str(bbox.class_id),
                    bounding_box=[bbox.x - bbox.w / 2, bbox.y - bbox.h / 2, bbox.w, bbox.h],
                )
                for bbox in label.bboxes
            ]
            class_label = str(label.bboxes[0].class_id) if label.bboxes else None

            sample = fo.Sample(
                filepath=str(image_path),
                label_path=str(label_path),
                ground_truth=fo.Detections(detections=detections),
                class_label=fo.Classification(label=class_label),
            )
            samples.append(sample)

        return samples

    def get_fiftyone_dataset(self) -> fo.Dataset:
        """
        Возвращает экземпляр :class:`fiftyone.Dataset` с загруженными
        сэмплами сплита.

        :return: Экземпляр :class:`fiftyone.Dataset`.
        :rtype: fiftyone.Dataset
        """
        samples = self.get_fiftyone_samples()

        # Формирование датасета FiftyOne
        dataset = fo.Dataset()
        dataset.add_samples(samples)
        return dataset

    def visualize(self) -> fo.Session:
        """
        Визуализирует сэмплы сплита в интерактивном приложении FiftyOne.

        :return: Экземпляр сессии FiftyOne с загруженными сэмплами сплита.
        :rtype: :class:`fiftyone.Session`
        """
        dataset = self.get_fiftyone_dataset()

        # Запуск интерактивного приложения
        session = fo.launch_app(dataset)
        return session

    def get_label_path(self, image_path: Path) -> Path:
        """
        Возвращает путь к метке для указанного изображения.

        :param image_path: Путь до изображения.
        :type image_path: pathlib.Path
        :return: Путь до метки.
        :rtype: Path
        """
        rel = image_path.relative_to(self.images_dir)
        return self.labels_dir / rel.with_suffix(".txt")
