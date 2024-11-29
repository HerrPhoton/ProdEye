import os
import shutil
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import yaml
from tqdm import tqdm


class YOLODatasetMerger:

    def __init__(self, source_dir: str, output_dir: str):
        """
        Инициализация мерджера датасетов YOLO

        Args:
            source_dir (str): Путь к исходной директории с датасетами
            output_dir (str): Путь к директории для объединенного датасета
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.classes = []
        self.stats = {
            'train': {
                'images': 0,
                'labels': 0
            },
            'valid': {
                'images': 0,
                'labels': 0
            },
            'test': {
                'images': 0,
                'labels': 0
            }
        }

        # Настройка логирования
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Создаем структуру выходных путей
        self.output_paths = self._create_output_structure()

    def _create_output_structure(self) -> dict:
        """Создает структуру директорий для выходного датасета"""
        output_paths = {
            'train': {
                'images': self.output_dir / 'train' / 'images',
                'labels': self.output_dir / 'train' / 'labels'
            },
            'valid': {
                'images': self.output_dir / 'valid' / 'images',
                'labels': self.output_dir / 'valid' / 'labels'
            },
            'test': {
                'images': self.output_dir / 'test' / 'images',
                'labels': self.output_dir / 'test' / 'labels'
            }
        }

        for split in output_paths.values():
            for path in split.values():
                path.mkdir(parents=True, exist_ok=True)

        return output_paths

    def _copy_file(self, src: Path, dst: Path) -> tuple[bool, Path]:
        """
        Копирует файл с обработкой конфликтов имен

        Args:
            src (Path): Путь к исходному файлу
            dst (Path): Путь назначения

        Returns:
            tuple[bool, Path]: (Успешность копирования, Итоговый путь файла)
        """
        if dst.exists():
            # Если файл с таким именем существует, создаем новое имя
            base, ext = dst.stem, dst.suffix
            counter = 1
            while dst.exists():
                dst = dst.parent / f"{base}_{counter}{ext}"
                counter += 1

        shutil.copy2(src, dst)
        return True, dst

    def _process_split(self, class_name: str, split: str, split_dir: Path):
        """Обрабатывает один сплит датасета"""
        for data_type in ['images', 'labels']:
            src_dir = split_dir / data_type
            if not src_dir.exists():
                continue

            for file in src_dir.glob('*.*'):
                dst = self.output_paths[split][data_type] / file.name

                # Копируем файл и получаем информацию о результате
                copied, final_path = self._copy_file(file, dst)

                # Если это изображение и оно было переименовано,
                # нужно также переименовать соответствующий файл меток
                if data_type == 'images' and final_path != dst:
                    # Находим соответствующий файл меток
                    label_src = split_dir / 'labels' / f"{file.stem}.txt"
                    if label_src.exists():
                        label_dst = self.output_paths[split]['labels'] / f"{final_path.stem}.txt"
                        shutil.copy2(label_src, label_dst)

                self.stats[split][data_type] += 1
                if final_path != dst:
                    self.logger.debug(f"Файл {file.name} был переименован в {final_path.name}")

    def merge(self, use_threads: bool = True):
        """
        Выполняет слияние датасетов

        Args:
            use_threads (bool): Использовать многопоточность для копирования
        """
        self.logger.info("Начинаем слияние датасетов...")

        # Собираем задачи для обработки
        tasks = []
        for class_name in os.listdir(self.source_dir):
            class_dir = self.source_dir / class_name
            if not class_dir.is_dir():
                continue

            self.classes.append(class_name)
            for split in ['train', 'valid', 'test']:
                split_dir = class_dir / split
                if not split_dir.exists():
                    continue
                tasks.append((class_name, split, split_dir))

        # Обработка задач
        if use_threads:
            with ThreadPoolExecutor() as executor:
                list(tqdm(executor.map(lambda x: self._process_split(*x), tasks), total=len(tasks), desc="Обработка датасетов"))
        else:
            for task in tqdm(tasks, desc="Обработка датасетов"):
                self._process_split(*task)

        self._create_yaml()
        self.logger.info("Слияние датасетов завершено!")
        self.print_stats()

    def _create_yaml(self):
        """Создает YAML файл для объединенного датасета"""
        yaml_content = {
            'path': str(self.output_dir.absolute()),
            'train': str(self.output_paths['train']['images'].relative_to(self.output_dir)),
            'val': str(self.output_paths['valid']['images'].relative_to(self.output_dir)),
            'test': str(self.output_paths['test']['images'].relative_to(self.output_dir)),
            'nc': len(self.classes),
            'names': sorted(self.classes)
        }

        with open(self.output_dir / 'dataset.yaml', 'w') as f:
            yaml.dump(yaml_content, f, sort_keys=False)

    def print_stats(self):
        """Выводит статистику по объединенному датасету"""
        self.logger.info("\nСтатистика объединенного датасета:")
        self.logger.info(f"Всего классов: {len(self.classes)}")
        self.logger.info("Классы: " + ", ".join(sorted(self.classes)))

        for split, data in self.stats.items():
            self.logger.info(f"\n{split.capitalize()}:")
            self.logger.info(f"  Изображений: {data['images']}")
            self.logger.info(f"  Меток: {data['labels']}")

    def verify_dataset(self) -> bool:
        """
        Проверяет целостность объединенного датасета

        Returns:
            bool: True если проверка прошла успешно
        """
        self.logger.info("Проверка целостности датасета...")

        for split in ['train', 'valid', 'test']:
            images = {f.stem for f in self.output_paths[split]['images'].glob('*.*')}
            labels = {f.stem for f in self.output_paths[split]['labels'].glob('*.*')}

            if images != labels:
                self.logger.error(f"Несоответствие в {split}:")
                self.logger.error(f"Изображения без меток: {images - labels}")
                self.logger.error(f"Метки без изображений: {labels - images}")
                return False

        self.logger.info("Проверка успешно завершена!")
        return True

    def cleanup(self):
        """Очищает выходную директорию"""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            self.logger.info(f"Директория {self.output_dir} очищена")
            self._create_output_structure()
