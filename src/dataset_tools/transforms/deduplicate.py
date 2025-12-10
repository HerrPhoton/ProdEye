from pathlib import Path
from collections.abc import Iterable

import fiftyone as fo
import fiftyone.brain as fob
from fiftyone.brain.similarity import SimilarityIndex

from ...utils import PathLike, normalize_to_paths
from ..structures import Split, YOLODataset


class DatasetDeduplicator:

    def __init__(self, dataset: fo.Dataset):
        self.dataset = dataset
        self.similarity_index: SimilarityIndex | None = None

    @classmethod
    def from_split_dirs(cls, split_dirs: PathLike | Iterable[PathLike]) -> 'DatasetDeduplicator':
        """Создает экземпляр DatasetDeduplicator из директорий сплитов.

        :param PathLike | Iterable[PathLike] split_dir: Путь/пути до директорий сплитов датасета
        :return DatasetDeduplicator: Экзмепляр DatasetDeduplicator, содержащий переданные сплиты
        """
        paths = normalize_to_paths(split_dirs)
        splits = [Split.from_dir(p) for p in paths]

        dataset = fo.Dataset()
        for split in splits:
            samples = split.get_fiftyone_samples()
            dataset.add_samples(samples)

        return cls(dataset)

    @classmethod
    def from_splits(cls, splits: Iterable[Split]) -> 'DatasetDeduplicator':
        """Создает экземпляр DatasetDeduplicator из экземляров Split.

        :param Iterable[Split] splits: Экземпляры сплитов датасета
        :return DatasetDeduplicator: Экзмепляр DatasetDeduplicator, содержащий переданные сплиты
        """
        splits = [Path(split.images_dir).parent for split in splits]

        dataset = fo.Dataset()
        for split in splits:
            samples = split.get_fiftyone_samples()
            dataset.add_samples(samples)

        return cls(dataset)

    @classmethod
    def from_dataset(cls, dataset: YOLODataset) -> 'DatasetDeduplicator':
        """Создает экземпляр DatasetDeduplicator из экземляра YOLODataset.

        :param YOLODataset dataset: Объект датасета YOLODataset
        :return DatasetDeduplicator: Экзмепляр DatasetDeduplicator, содержащий сплиты из датасета
        """
        fo_dataset = dataset.get_fiftyone_dataset()
        return cls(fo_dataset)

    @classmethod
    def from_yaml(cls, data_yaml: PathLike) -> 'DatasetDeduplicator':
        """Создает экземпляр DatasetDeduplicator на основе конфигурации data.yaml.

        :param PathLike data_yaml: Путь до data.yaml датасета
        :return DatasetDeduplicator: Инициализированный экземпляр DatasetDeduplicator со сплитами из data.yaml
        """
        dataset = YOLODataset.from_yaml(data_yaml)
        fo_dataset = dataset.get_fiftyone_dataset()
        return cls(fo_dataset)

    def find_duplicates(
        self,
        model: str = "clip-vit-base32-torch",
        threshold: float = 0.2,
        batch_size: int | None = None,
        num_workers: int | None = None,
    ) -> dict[str, list[str]]:
        """Выполняет обнаружение дубликатов изображений в датасете на основе эмбеддингов,
        сгенерированных моделью. Дубликатами считаются пары сэмплов, евклидово расстояние между
        эмбеддингами которых не превышает указанный порог.

        :param str model: Модель для создания эмбеддингов сэмплов (из списка `fiftyone.zoo.list_zoo_models()`)
        :param float threshold: Порог нормализированного евклидова расстояния между эмбеддингами (0.0-1.0)
        :param int batch_size: Размер батча при генерации эмбеддингов
        :param int num_workers: Число воркеров для параллельной обработки
        :return dict[str, list[str]]:
            Словарь вида ``{ original_filepath: [duplicate_filepath, ...] }``, где ключ —
            путь к исходному изображению, а значение — список путей ко всем найденным
            дубликатам
        """
        # Поиск дубликатов
        self.similarity_index = fob.compute_near_duplicates(
            self.dataset,
            model=model,
            threshold=threshold,
            batch_size=batch_size,
            num_workers=num_workers
        )
        self.similarity_index.find_duplicates(threshold)

        # Формирование словаря с дубликатами
        duplicates_map: dict[str, list[str]] = {}
        for original_id, neighbors in self.similarity_index.neighbors_map.items():
            original_path = self.dataset[original_id].filepath
            duplicate_paths = [self.dataset[dup_id].filepath for dup_id, _ in neighbors]

            if duplicate_paths:
                duplicates_map[original_path] = duplicate_paths

        return duplicates_map

    def delete_duplicates(self) -> list[tuple[str, str]]:
        """Удаляет найденные дулбикаты сэмплов.

        :raises RuntimeError: Если метод вызван до выполнения `find_duplicates`
        :return list[tuple[str, str]]: Список путей к удаленным сэмплам (путь до изображения, путь до метки)
        """
        if self.similarity_index is None:
            raise RuntimeError("Duplicates have not been calculated. First, call find_duplicates().")

        removed_samples: list[tuple[str, str]] = []
        for duplicate_id in self.similarity_index.duplicate_ids:
            sample = self.dataset[duplicate_id]

            # Удаляем изображение
            image_path = Path(sample.filepath)
            image_path.unlink()

            # Удаляем метку
            label_path = Path(sample.get_field("label_path"))
            label_path.unlink()

            removed_samples.append((str(image_path), str(label_path)))

            # Удаляем сэмпл из датасета FiftyOne
            self.dataset.delete_samples([duplicate_id])

        return removed_samples

    def visualize_duplicates(self, compute_visualization: bool = False) -> fo.Session:
        """Визуализирует найденные дубликаты в интерактивном приложении FiftyOne.

        При необходимости метод может дополнительно вычислить двумерное представление
        эмбеддингов с использованием UMAP. В этом случае в приложении FiftyOne в панели
        *Embeddings* появится новое представление с ключом ``"duplicate_embeddings"``.

        :param bool compute_visualization: Если ``True``, вычисляет двумерное представление эмбеддингов (UMAP) и сохраняет
            его в датасет под ключом ``"duplicate_embeddings"`` для визуализации в интерфейсе FiftyOne
        :raises RuntimeError: Если метод вызван до выполнения `find_duplicates`
        :return fiftyone.Session: Экземпляр сессии FiftyOne с найденными дубликатами
        """
        if self.similarity_index is None:
            raise RuntimeError("Duplicates have not been calculated. First, call find_duplicates().")

        # Вычисление 2D-представления эмбеддингов для визуализации
        if compute_visualization:
            fob.compute_visualization(
                samples=self.dataset,
                similarity_index=self.similarity_index,
                num_dims=2,
                method="umap",
                brain_key="duplicate_embeddings",
                create_index=True
            )

        # Визуализация групп дубликатов с категориальными метками
        view = self.similarity_index.duplicates_view(type_field="duplicate_status")
        return fo.launch_app(view)
