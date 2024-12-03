import os
from typing import Literal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
import fiftyone as fo
import fiftyone.zoo as foz
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity


class DuplicatesHandler:
    """Класс для поиска и удаления дубликатов изображений в датасетах."""

    def __init__(self,
                 dataset_path: str,
                 dataset_type: Literal["dir", "yolo"] = "dir",
                 split: Literal["train", "valid", "test"] | list[Literal["train", "valid", "test"]] = "all",
                 similarity_threshold: float = 0.99,
                 yaml_filename: str = "data.yaml",
                 device: Literal["cpu", "gpu"] = "gpu",
                 embeddings_batch_size: int = 64,
                 similarity_batch_size: int = 1024):
        """
        Args:
            dataset_path: путь к датасету (абсолютный или относительный)
            dataset_type: тип датасета ("dir" или "yolo")
            similarity_threshold: порог схожести изображений (0-1)
            yaml_filename: имя yaml файла для YOLO датасета
            device: устройство для обучения ("cpu" или "gpu")
            embeddings_batch_size: размер батча для вычисления эмбеддингов
            similarity_batch_size: размер батча для вычисления матрицы сходства
        """
        self.dataset_path = str(Path(dataset_path).resolve())
        self.dataset_type = dataset_type.lower()
        self.similarity_threshold = similarity_threshold
        self.yaml_filename = yaml_filename
        self.dataset = None
        self.duplicates = None
        self.device = device.lower()
        self.embeddings_batch_size = embeddings_batch_size
        self.similarity_batch_size = similarity_batch_size

        if self.dataset_type not in ["dir", "yolo"]:
            raise ValueError("dataset_type должен быть 'dir' или 'yolo'")

        if isinstance(split, str):
            split = [split]

        elif isinstance(split, list):
            if not all(s in ["train", "valid", "test"] for s in split):
                raise ValueError("split должен быть 'train', 'valid', 'test' или список из них")

        else:
            raise ValueError("split должен быть 'train', 'valid', 'test' или список из них")

        if "all" in split:
            split = ['train', 'valid', 'test']

        if self.device == "gpu" and not torch.cuda.is_available():
            print("GPU недоступна, запуск будет осуществлен на CPU")
            self.device = "cpu"

        self._load_dataset(split)

    def _load_dataset(self, splits: list[Literal["train", "valid", "test"]]) -> None:
        """Загружает датасет в fiftyone."""
        if self.dataset_type == "yolo":
            self.dataset = fo.Dataset()

            for split in splits:
                split_images_path = os.path.join(self.dataset_path, split, 'images')

                if os.path.exists(split_images_path):

                    split_dataset = fo.Dataset.from_dir(dataset_dir=split_images_path,
                                                        dataset_type=fo.types.ImageDirectory,
                                                        tags=[split])

                    if len(split_dataset):
                        self.dataset.add_samples(split_dataset)

            if len(self.dataset) == 0:
                raise ValueError("Не найдено изображений в датасете")
        else:
            self.dataset = fo.Dataset.from_dir(dataset_dir=self.dataset_path, dataset_type=fo.types.ImageDirectory)

    def find_duplicates(self) -> dict:
        """Находит дубликаты изображений в датасете путем создания эмбеддингов и
        определения косинусного расстояния между ними.

        Returns:
            Dict: словарь с группами дубликатов
        """
        self.dataset.add_sample_field("duplicate_group", fo.IntField, description="Индекс группы дубликатов")

        model = foz.load_zoo_model("resnet18-imagenet-torch", batch_size=self.embeddings_batch_size)
        embeddings = self.dataset.compute_embeddings(model)

        if torch.cuda.is_available() and self.device == "gpu":

            embeddings_tensor = torch.tensor(embeddings)
            similarity_matrix = np.zeros((len(embeddings), len(embeddings)))

            for i in tqdm(range(0, len(embeddings), self.similarity_batch_size), desc="Вычисление сходства на GPU"):
                batch_end = min(i + self.similarity_batch_size, len(embeddings))
                batch = embeddings_tensor[i : batch_end].cuda()

                for j in range(0, len(embeddings), self.similarity_batch_size):
                    j_end = min(j + self.similarity_batch_size, len(embeddings))
                    other_batch = embeddings_tensor[j : j_end].cuda()

                    batch_norm = torch.nn.functional.normalize(batch, p=2, dim=1)
                    other_norm = torch.nn.functional.normalize(other_batch, p=2, dim=1)
                    sim = torch.mm(batch_norm, other_norm.t()).cpu().numpy()

                    similarity_matrix[i : batch_end, j : j_end] = sim

                    del other_batch
                    torch.cuda.empty_cache()

                del batch
                torch.cuda.empty_cache()
        else:
            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                similarity_matrix = np.zeros((len(embeddings), len(embeddings)))

                def compute_similarities(i):
                    similarities = cosine_similarity([embeddings[i]], embeddings)[0]
                    similarities[i] = 0
                    return i, similarities

                futures = []
                for i in range(len(embeddings)):
                    futures.append(executor.submit(compute_similarities, i))

                for future in tqdm(futures, total=len(futures), desc="Вычисление сходства"):
                    i, similarities = future.result()
                    similarity_matrix[i] = similarities

        similarity_matrix = similarity_matrix - np.identity(len(similarity_matrix))
        id_map = [s.id for s in self.dataset.select_fields(["id"])]

        self.duplicates = {}
        current_group = 0
        processed_files = set()

        for idx, sample in enumerate(tqdm(self.dataset.iter_samples(), total=len(self.dataset), desc="Поиск дубликатов")):
            if sample.filepath not in processed_files:
                dup_idxs = np.where(similarity_matrix[idx] > self.similarity_threshold)[0]

                if len(dup_idxs) > 0:
                    group = [sample.filepath]
                    processed_files.add(sample.filepath)

                    sample.tags.append("has_duplicates")
                    sample.duplicate_group = current_group
                    sample.save()

                    for dup_idx in dup_idxs:
                        dup_sample = self.dataset[id_map[dup_idx]]

                        if dup_sample.filepath not in processed_files:
                            group.append(dup_sample.filepath)
                            processed_files.add(dup_sample.filepath)

                            dup_sample.tags.append("duplicate")
                            dup_sample.duplicate_group = current_group
                            dup_sample.save()

                    if len(group) > 1:
                        self.duplicates[current_group] = group
                        current_group += 1

        self.dataset.save()

    def view_duplicates(self, auto_launch: bool = True) -> None:
        """Открывает интерактивный просмотр дубликатов в веб-интерфейсе fiftyone.

        Args:
            auto_launch: автоматически открыть браузер
        """
        if self.duplicates is None:
            raise ValueError("Сначала выполните поиск дубликатов методом find_duplicates()")

        view = self.dataset.match_tags(["has_duplicates", "duplicate"]).sort_by("duplicate_group")
        fo.launch_app(self.dataset, view=view)

    def remove_duplicates(self, keep_first: bool = True) -> None:
        """Удаляет найденные дубликаты изображений.

        Args:
            keep_first: сохранять первое изображение из группы дубликатов
        """
        if self.duplicates is None:
            raise ValueError("Сначала выполните поиск дубликатов методом find_duplicates()")

        for group in self.duplicates.values():
            start_idx = 1 if keep_first else 0

            for img_path in group[start_idx :]:
                view = self.dataset.match({"filepath": img_path})
                sample = view.first()

                if sample:
                    self.dataset.delete_samples(sample.id)

                full_path = os.path.join(self.dataset_path, img_path)
                if os.path.exists(full_path):
                    os.remove(full_path)

                if self.dataset_type == "yolo":
                    label_path = Path(full_path).with_suffix('.txt')
                    if label_path.exists():
                        label_path.unlink()

        self.dataset.save()

    def get_duplicate_groups(self) -> dict | None:
        """Возвращает найденные группы дубликатов.

        Returns:
            Dict: словарь с группами дубликатов или None, если поиск еще не выполнялся
        """
        return self.duplicates

    def get_duplicate_count(self) -> int:
        """Возвращает количество найденных групп дубликатов.

        Returns:
            int: количество групп дубликатов
        """
        return len(self.duplicates) if self.duplicates else 0
