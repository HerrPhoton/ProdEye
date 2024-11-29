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
                 split: Literal["train", "valid", "test", "all"] = "all",
                 similarity_threshold: float = 0.99,
                 yaml_filename: str = "data.yaml"):
        """
        Args:
            dataset_path: путь к датасету (абсолютный или относительный)
            dataset_type: тип датасета ("dir" или "yolo")
            similarity_threshold: порог схожести изображений (0-1)
            yaml_filename: имя yaml файла для YOLO датасета
        """
        self.dataset_path = str(Path(dataset_path).resolve())
        self.dataset_type = dataset_type.lower()
        self.similarity_threshold = similarity_threshold
        self.yaml_filename = yaml_filename
        self.dataset = None
        self.duplicates = None

        if self.dataset_type not in ["dir", "yolo"]:
            raise ValueError("dataset_type должен быть 'dir' или 'yolo'")

        if split not in ["train", "valid", "test", "all"]:
            raise ValueError("split должен быть 'train', 'valid', 'test' или 'all'")

        self._load_dataset(split)

    def _load_dataset(self, split: Literal["train", "valid", "test", "all"]) -> None:
        """Загружает датасет в fiftyone."""
        if self.dataset_type == "yolo":
            self.dataset = fo.Dataset()

            splits = ['train', 'valid', 'test'] if split == 'all' else [split]
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

        model = foz.load_zoo_model("mobilenet-v2-imagenet-torch")
        embeddings = self.dataset.compute_embeddings(model)

        if torch.cuda.is_available():
            embeddings_tensor = torch.tensor(embeddings).cuda()
            similarity_matrix = torch.nn.functional.cosine_similarity(embeddings_tensor.unsqueeze(1),
                                                                      embeddings_tensor.unsqueeze(0),
                                                                      dim=2).cpu().numpy()
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
                # Удаляем изображение
                full_path = os.path.join(self.dataset_path, img_path)
                if os.path.exists(full_path):
                    os.remove(full_path)

                # Если это YOLO датасет, удаляем также соответствующий label-файл
                if self.dataset_type == "yolo":
                    label_path = Path(full_path).with_suffix('.txt')
                    if label_path.exists():
                        label_path.unlink()

                # Удаляем образец из датасета fiftyone
                self.dataset.delete_samples(img_path)

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
