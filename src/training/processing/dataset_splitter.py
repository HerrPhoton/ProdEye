import os
import random
import shutil
from pathlib import Path


class DatasetSplitter:

    def __init__(self, images_dir: str, labels_dir: str):
        """
        Инициализация сплиттера датасета

        Args:
            images_dir: путь к директории с изображениями
            labels_dir: путь к директории с метками
        """
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir)

        if not self.images_dir.exists() or not self.labels_dir.exists():
            raise ValueError("Указанные директории не существуют")

        self.image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

    def split_dataset(self, output_dir: str, val_size: int | float) -> tuple[int, int]:
        """
        Разделение датасета на train и valid части

        Args:
            output_dir: директория для сохранения разделенного датасета
            val_size: количество изображений или доля для валидационной выборки

        Returns:
            Tuple[int, int]: количество файлов в train и valid наборах
        """

        output_path = Path(output_dir)

        for split in ['train', 'valid']:
            for subdir in ['images', 'labels']:
                (output_path / split / subdir).mkdir(parents=True, exist_ok=True)

        if isinstance(val_size, float):
            if not 0 < val_size < 1:
                raise ValueError("Доля должна быть между 0 и 1")

            val_count = int(len(self.image_files) * val_size)

        else:
            if not 0 < val_size < len(self.image_files):
                raise ValueError("Количество файлов некорректно")

            val_count = val_size

        val_files = random.sample(self.image_files, val_count)
        train_files = [f for f in self.image_files if f not in val_files]

        for file in train_files:
            base_name = os.path.splitext(file)[0]
            shutil.copy2(self.images_dir / file, output_path / 'train' / 'images' / file)
            label_file = f"{base_name}.txt"

            if (self.labels_dir / label_file).exists():
                shutil.copy2(self.labels_dir / label_file, output_path / 'train' / 'labels' / label_file)

        for file in val_files:
            base_name = os.path.splitext(file)[0]
            shutil.copy2(self.images_dir / file, output_path / 'valid' / 'images' / file)
            label_file = f"{base_name}.txt"

            if (self.labels_dir / label_file).exists():
                shutil.copy2(self.labels_dir / label_file, output_path / 'valid' / 'labels' / label_file)
