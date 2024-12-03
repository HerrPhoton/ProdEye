import os
import random


class DatasetCleaner:

    def __init__(self, images_dir, labels_dir, verbose=True):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.verbose = verbose

    def get_file_pairs(self):
        """Получение списков файлов изображений и их меток"""
        image_files = {f.split('.')[0] for f in os.listdir(self.images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))}

        label_files = {f.split('.')[0] for f in os.listdir(self.labels_dir) if f.endswith('.txt')}

        return image_files, label_files

    def remove_unpaired(self):
        """Удаление изображений без меток и меток без изображений"""
        image_files, label_files = self.get_file_pairs()

        for img in image_files - label_files:
            img_path = self._find_image_path(img)

            if img_path:
                os.remove(img_path)

                if self.verbose:
                    print(f"Удалено изображение без метки: {img_path}")

        for label in label_files - image_files:
            label_path = os.path.join(self.labels_dir, f"{label}.txt")
            os.remove(label_path)

            if self.verbose:
                print(f"Удалена метка без изображения: {label_path}")

    def remove_images_without_labels(self):
        """Удаление изображений без меток"""
        image_files, label_files = self.get_file_pairs()

        for img in image_files - label_files:
            img_path = self._find_image_path(img)

            if img_path:
                os.remove(img_path)

                if self.verbose:
                    print(f"Удалено изображение без метки: {img_path}")

    def remove_labels_without_images(self):
        """Удаление меток без изображений"""
        image_files, label_files = self.get_file_pairs()

        for label in label_files - image_files:
            label_path = os.path.join(self.labels_dir, f"{label}.txt")
            os.remove(label_path)

            if self.verbose:
                print(f"Удалена метка без изображения: {label_path}")

    def reduce_dataset(self, target_size):
        """Сокращение датасета до указанного размера"""
        image_files, label_files = self.get_file_pairs()
        paired_files = image_files & label_files

        if len(paired_files) <= target_size:
            if self.verbose:
                print("Размер датасета уже меньше или равен целевому размеру")
            return

        files_to_remove = random.sample(list(paired_files), len(paired_files) - target_size)

        for file in files_to_remove:
            img_path = self._find_image_path(file)
            label_path = os.path.join(self.labels_dir, f"{file}.txt")

            if img_path:
                os.remove(img_path)

            os.remove(label_path)

            if self.verbose:
                print(f"Удалена пара файлов: {file}")

    def _find_image_path(self, filename):
        """Поиск пути к изображению с учетом разных расширений"""
        for ext in ['.jpg', '.jpeg', '.png']:
            path = os.path.join(self.images_dir, f"{filename}{ext}")

            if os.path.exists(path):
                return path

        return None
