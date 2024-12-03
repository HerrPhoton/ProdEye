from pathlib import Path


class BackgroundHandler:

    def __init__(self, images_dir: str, labels_dir: str):
        """
        Инициализация создателя пустых меток

        Args:
            images_dir: путь к директории с изображениями
            labels_dir: путь к директории с метками
        """
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir)

        if not self.images_dir.exists():
            raise ValueError("Директория с изображениями не существует")

        self.labels_dir.mkdir(parents=True, exist_ok=True)

        self.image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')

    def create_empty_labels(self, skip_existing: bool = True) -> tuple[int, list[str]]:
        """
        Создание пустых меток для всех изображений

        Args:
            skip_existing: пропускать ли файлы с уже существующими метками

        Returns:
            tuple[int, List[str]]: количество созданных меток и список пропущенных файлов
        """
        created_count = 0
        skipped_files = []

        for img_file in self.images_dir.iterdir():
            if img_file.suffix.lower() in self.image_extensions:

                label_file = self.labels_dir / f"{img_file.stem}.txt"

                if label_file.exists() and skip_existing:
                    skipped_files.append(str(img_file.name))
                    continue

                label_file.touch()
                created_count += 1

        return created_count, skipped_files

    def get_unlabeled_images(self) -> list[str]:
        """
        Получение списка изображений без меток

        Returns:
            List[str]: список имен файлов изображений без меток
        """
        unlabeled = []

        for img_file in self.images_dir.iterdir():
            if img_file.suffix.lower() in self.image_extensions:
                label_file = self.labels_dir / f"{img_file.stem}.txt"
                if not label_file.exists():
                    unlabeled.append(img_file.name)

        return unlabeled

    def get_background_ratio(self) -> float:
        """
        Подсчет доли background изображений в датасете

        Returns:
            float: доля background изображений (0-1)
        """

        total_count = 0
        background_count = 0

        for label_file in self.labels_dir.iterdir():
            if label_file.suffix == '.txt':
                total_count += 1

                if label_file.stat().st_size == 0:
                    background_count += 1

        return background_count / total_count if total_count > 0 else 0
