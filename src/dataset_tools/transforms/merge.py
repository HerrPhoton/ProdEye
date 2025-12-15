import shutil
from typing import Literal
from pathlib import Path
from collections.abc import Mapping, Iterable

from tqdm import tqdm

from ...utils import PathLike, normalize_to_paths
from ..handlers import YOLOLabelHandler
from ..structures import Split, YOLODataset


class DatasetMerger:

    def __init__(self, data_yaml: Iterable[PathLike]):
        """
        Инициализирует датасеты для объединения. Создает экземпляры :class:`YOLODataset` из конфигураций data.yaml.

        :param data_yaml: Пути до data.yaml каждого датасета
        :type data_yaml: Iterable[PathLike]
        """
        paths = normalize_to_paths(data_yaml)
        self.datasets: list[YOLODataset] = [YOLODataset.from_yaml(p) for p in paths]

    @classmethod
    def from_datasets(cls, datasets: Iterable[YOLODataset]) -> 'DatasetMerger':
        """
        Создает экземпляр :class:`DatasetMerger` из экземляров :class:`YOLODataset`.

        :param datasets: Объекты датасетов :class:`YOLODataset` для слияния.
        :type datasets: Iterable[YOLODataset]
        :return: Экзмепляр :class:`DatasetMerger`, содержащий переданные датасеты.
        :rtype: DatasetMerger
        """
        merger = cls.__new__(cls)
        merger.datasets = list(datasets)
        return merger

    def merge(
        self,
        output_dir: PathLike,
        progress_bar: bool = True,
        on_conflict: Literal["skip", "exception", "rename"] = "rename",
    ) -> YOLODataset:
        """
        Объединяет датасеты по их сплитам. Сохраняет объединенный датасет в указанную директорию.

        Если ``output_dir`` является одим из объединяемых датасетов, то индексы его классов берутся за основу,
        а индексы классов из других датасетов настраиваются относительно основного датасета. Если ``output_dir``
        не является одним из объединяемых датасетов, то в качестве основы используется первый датасет в списке.

        Если при копировании сэмплов в одну директорию сплита имена сэмплов будут совпадать, то конфликт будет
        разрешен согласно выбранной стратегии:
        - ``skip``: пропустить конфликтующий сэмпл
        - ``exception``: вызвать исключение
        - ``rename``: переименовать конфликтующий сэмпл, добавив числовой суффикс к имени (например, ``name.jpg -> name_1.jpg``)

        :param output_dir: Директория для сохранения объединенного датасета.
        :type output_dir: PathLike
        :param progress_bar: Включить ли индикатор выполнения объединения. Шаг соответсвует копированию сэмпла.
        :type progress_bar: bool, optional
        :param on_conflict: Стратегия обработки при конфликте имен.
        :type on_conflict: Literal["skip", "exception", "rename"], optional
        :return: Экземпляр :class:`YOLODataset` с объединенными сплитами.
        :rtype: YOLODataset
        """
        output_dir = Path(output_dir)
        merged_classes, merged_splits = self._get_base_dataset(output_dir)

        # Подсчет общего количества сэмплов для прогресс-бара
        total_samples = sum(sum(d.count_samples().values()) for d in self.datasets)

        # Объединение сплитов
        with tqdm(total=total_samples, desc="Объединение датасетов", disable=not progress_bar) as pbar:
            for dataset in self.datasets:
                for split_name, split in dataset.splits.items():

                    # Получить сплит в объединенном датасете
                    images_dir, labels_dir = self._ensure_split_dirs(
                        output_dir=output_dir,
                        split_name=split_name,
                        merged_splits=merged_splits
                    )

                    # Скопировать сэмплы
                    for image_path, label_path in split.iter_samples():
                        new_img_path, new_lbl_path = self._copy_sample(
                            image_path=image_path,
                            label_path=label_path,
                            images_dir=images_dir,
                            labels_dir=labels_dir,
                            on_conflict=on_conflict,
                            pbar=pbar
                        )

                        if new_img_path is None:
                            continue

                    # Обновить индексы классов в метках
                    self._update_class_indices(
                        labels_dir=labels_dir,
                        dataset_classes=dataset.class_names,
                        merged_classes=merged_classes
                    )

        # Инициализировать объединенный датасет и записать data.yaml
        merged_dataset = YOLODataset(
            root=output_dir,
            data_yaml=output_dir / "data.yaml",
            num_classes=len(merged_classes),
            class_names=merged_classes,
            splits=merged_splits,
        )
        merged_dataset.write_data_yaml()

        return merged_dataset

    def _update_class_indices(
        self,
        labels_dir: Path,
        dataset_classes: Mapping[int, str],
        merged_classes: dict[int, str],
    ) -> None:
        """
        Обновляет индексы классов в метках согласно объединенным классам.

        :param labels_dir: Директория с метками.
        :type labels_dir: pathlib.Path
        :param dataset_classes: Классы текущего датасета.
        :type dataset_classes: Mapping[int, str]
        :param merged_classes: Объединенные классы (изменяется in-place).
        :type merged_classes: dict[int, str]
        """
        # Инвертировать ключи со значениями для быстрого поиска индексов по названиям классов
        inverted_merged_idx = {name: idx for idx, name in merged_classes.items()}
        inverted_dataset_idx = {name: idx for idx, name in dataset_classes.items()}

        # Определить замены индексов
        new_classes: dict[int, int] = {}
        for class_name, class_id in inverted_dataset_idx.items():
            if class_name in inverted_merged_idx:
                # Если класс объединяемого датасета уже есть, то использовать существующий индекс
                merged_id = inverted_merged_idx[class_name]
                if merged_id != class_id:
                    new_classes[class_id] = merged_id
            else:
                # Если класса объединяемого датасета нет, то добавить его в основные классы с последним индексом
                new_id = max(merged_classes.keys()) + 1
                merged_classes[new_id] = class_name
                new_classes[class_id] = new_id

        # Обновить индексы классов в метках
        if new_classes:
            handler = YOLOLabelHandler(labels_dir)
            handler.set_classes(new_classes)

    def _copy_sample(
        self,
        image_path: Path,
        label_path: Path,
        images_dir: Path,
        labels_dir: Path,
        on_conflict: Literal["skip", "exception", "rename"],
        pbar: tqdm | None,
    ) -> tuple[Path | None, Path | None]:
        """
        Копирует сэмпл с обработкой конфликтов имен.

        :param image_path: Путь к исходному изображению.
        :type image_path: pathlib.Path
        :param label_path: Путь к исходной метке.
        :type label_path: pathlib.Path
        :param images_dir: Целевая директория для изображений.
        :type images_dir: pathlib.Path
        :param labels_dir: Целевая директория для меток.
        :type labels_dir: pathlib.Path
        :param on_conflict: Стратегия обработки конфликтов.
        :type on_conflict: Literal["skip", "exception", "rename"]
        :param pbar: Прогресс-бар.
        :type pbar: tqdm | None
        :raises FileExistsError: Если при переименовании и ``on_conflict=exception`` сэмплы имеют
            одинаковые имена с уже существующими сэмплами.
        :return: Пути к скопированным файлам или None при ``on_conflict=skip``.
        :rtype: tuple[Path | None, Path | None]
        """
        new_img_path = images_dir / image_path.name
        new_lbl_path = labels_dir / label_path.name

        if new_img_path.exists() or new_lbl_path.exists():
            match on_conflict:
                case "skip":
                    if pbar:
                        pbar.update(1)
                    return None, None

                case "exception":
                    raise FileExistsError(
                        f"Сэмпл {new_img_path}, {new_lbl_path} уже существует"
                    )

                case "rename":
                    new_img_path = self._get_unique_path(new_img_path)
                    new_lbl_path = labels_dir / f"{new_img_path.stem}{new_lbl_path.suffix}"

        shutil.copy(image_path, new_img_path)
        shutil.copy(label_path, new_lbl_path)

        if pbar:
            pbar.update(1)

        return new_img_path, new_lbl_path

    def _ensure_split_dirs(
        self,
        output_dir: Path,
        split_name: str,
        merged_splits: dict[str, Split]
    ) -> tuple[Path, Path]:
        """
        Создает директории для сплита, если они еще не созданы.

        :param output_dir: Директория для сохранения объединенного датасета.
        :type output_dir: pathlib.Path
        :param split_name: Имя сплита.
        :type split_name: str
        :param merged_splits: Словарь существующих сплитов.
        :type merged_splits: dict[str, Split]
        :return: Пути к директориям ``images`` и ``labels``.
        :rtype: tuple[pathlib.Path, pathlib.Path]
        """
        # Для нерассмотренного сплита создать директории в датасете
        if split_name not in merged_splits:
            images_dir = output_dir / split_name / "images"
            labels_dir = output_dir / split_name / "labels"

            images_dir.mkdir(parents=True, exist_ok=True)
            labels_dir.mkdir(parents=True, exist_ok=True)

            merged_splits[split_name] = Split(
                name=split_name,
                images_dir=images_dir,
                labels_dir=labels_dir,
            )
        else:
            images_dir = merged_splits[split_name].images_dir
            labels_dir = merged_splits[split_name].labels_dir

        return images_dir, labels_dir

    def _get_base_dataset(self, output_dir: Path) -> tuple[dict[int, str], dict[str, Split]]:
        """
        Определяет базовый датасет и начальные классы для объединения.

        :param output_dir: Директория для сохранения объединенного датасета.
        :type output_dir: pathlib.Path
        :return: Словарь с индексами и словарь со сплитами базового класса.
        :rtype: tuple[dict[int, str], dict[str, Split]]
        """
        merged_classes: dict[str, int] = self.datasets[0].class_names.copy()
        merged_splits: dict[str, Split] = {}

        # Если выходной директорией указан один из датасетов,
        # то берем его индексы классов за основу
        for dataset in self.datasets:
            if output_dir.resolve() == dataset.root.resolve():
                merged_classes = dataset.class_names.copy()
                merged_splits = dataset.splits.copy()
                self.datasets.remove(dataset)
                break

        return merged_classes, merged_splits

    def _get_unique_path(self, base_path: Path) -> Path:
        """
        Генерирует уникальный путь к файлу, добавляя числовой суффикс при конфликте.

        :param base_path: Базовый путь к файлу.
        :type base_path: pathlib.Path
        :return: Уникальный путь к файлу.
        :rtype: pathlib.Path
        """
        if not base_path.exists():
            return base_path

        # Пытаемся найти свободное имя, добавляя числовой суффикс
        counter = 1
        while True:
            new_name = f"{base_path.stem}_{counter}{base_path.suffix}"
            new_path = base_path.parent / new_name

            if not new_path.exists():
                return new_path

            counter += 1
