import os
from pathlib import Path

from PIL import Image
from icrawler.builtin import BingImageCrawler
from icrawler.builtin import GoogleImageCrawler

from .images_renamer import ImagesRenamer
from .duplicates_handler import DuplicatesHandler


class ImageScrapper:
    """Класс для скачивания изображений из Google и Bing."""

    def __init__(self,
                 timeout: int = 15,
                 max_retries: int = 5,
                 min_size: tuple[int, int] = (640, 640),
                 threads: tuple[int, int, int] = (2, 2, 4)):

        self.crawler_settings = {
            'timeout': timeout,
            'max_retries': max_retries,
            'min_size': min_size,
            'max_size': None,
        }

        self.feeder_threads, self.parser_threads, self.downloader_threads = threads

    def _setup_crawler(self, crawler_class, storage_dir: str) -> object:
        """Настройка краулера с заданными параметрами.

        Args:
            crawler_class: Класс краулера (GoogleImageCrawler или BingImageCrawler)
            storage_dir (str): Директория для сохранения
        """
        crawler = crawler_class(storage={'root_dir': storage_dir},
                                feeder_threads=self.feeder_threads,
                                parser_threads=self.parser_threads,
                                downloader_threads=self.downloader_threads,
                                log_level=50)

        crawler.downloader.timeout = self.crawler_settings['timeout']
        crawler.downloader.max_retries = self.crawler_settings['max_retries']

        return crawler

    def _create_directory(self, path: str) -> bool:
        """Создание директории для сохранения изображений."""

        try:
            os.makedirs(path, exist_ok=True)
            return True

        except Exception as e:
            print(f'Ошибка при создании директории {path}: {e}')
            return False

    def _remove_corrupted_images(self, directory: str) -> None:
        """Удаляет поврежденные изображения из директории.

        Args:
            directory (str): Путь к директории с изображениями
        """
        for img_path in Path(directory).glob('*'):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:

                try:
                    with Image.open(img_path) as img:
                        img.verify()

                except Exception as e:
                    print(f'Удаление поврежденного изображения {img_path}: {str(e)}')
                    img_path.unlink()

    def scrap(self,
              queries: str | list[str],
              output_dir: str | None = None,
              group: str | None = None,
              limit: int = 10,
              remove_duplicates: bool = True) -> None:
        """
        Скачивание изображений из Google и Bing.
        """
        output_dir = output_dir or os.path.dirname(os.path.abspath(__file__))

        if isinstance(queries, str):
            queries = [queries]

        if group:
            group = group.strip().lower()
            target_dir = os.path.join(output_dir, group)

            if not self._create_directory(target_dir):
                return

            per_query_limit = limit // len(queries)

            for idx, query in enumerate(queries):
                query = query.strip().lower()
                base_offset = idx * per_query_limit

                try:
                    google_crawler = self._setup_crawler(GoogleImageCrawler, target_dir)
                    google_crawler.crawl(keyword=query,
                                         max_num=per_query_limit // 2,
                                         min_size=self.crawler_settings['min_size'],
                                         max_size=self.crawler_settings['max_size'],
                                         file_idx_offset=base_offset)
                except Exception as e:
                    print(f'Ошибка при скачивании с Google для запроса "{query}": {str(e)}')

                try:
                    bing_crawler = self._setup_crawler(BingImageCrawler, target_dir)
                    bing_crawler.crawl(keyword=query,
                                       max_num=per_query_limit // 2,
                                       min_size=self.crawler_settings['min_size'],
                                       max_size=self.crawler_settings['max_size'],
                                       file_idx_offset=base_offset + per_query_limit // 2)
                except Exception as e:
                    print(f'Ошибка при скачивании с Bing для запроса "{query}": {str(e)}')

            self._remove_corrupted_images(target_dir)

            if remove_duplicates:
                duplicates_handler = DuplicatesHandler(dataset_path=target_dir, dataset_type="dir", similarity_threshold=0.98)

                duplicates_handler.find_duplicates()
                duplicates_handler.remove_duplicates()

            renamer = ImagesRenamer(images_dir=target_dir, new_name=group)
            renamer.rename_images()

        else:
            for query in queries:
                query = query.strip().lower()
                query_dir = os.path.join(output_dir, query)

                if not self._create_directory(query_dir):
                    continue

                try:
                    google_crawler = self._setup_crawler(GoogleImageCrawler, query_dir)
                    google_crawler.crawl(keyword=query,
                                         max_num=limit // 2,
                                         min_size=self.crawler_settings['min_size'],
                                         max_size=self.crawler_settings['max_size'],
                                         file_idx_offset=0)

                except Exception as e:
                    print(f'Ошибка при скачивании с Google для запроса "{query}": {str(e)}')

                try:
                    bing_crawler = self._setup_crawler(BingImageCrawler, query_dir)
                    bing_crawler.crawl(keyword=query,
                                       max_num=limit // 2,
                                       min_size=self.crawler_settings['min_size'],
                                       max_size=self.crawler_settings['max_size'],
                                       file_idx_offset=limit // 2)
                except Exception as e:
                    print(f'Ошибка при скачивании с Bing для запроса "{query}": {str(e)}')

                self._remove_corrupted_images(query_dir)

                if remove_duplicates:
                    duplicates_handler = DuplicatesHandler(dataset_path=query_dir,
                                                           dataset_type="dir",
                                                           similarity_threshold=0.98)

                    duplicates_handler.find_duplicates()
                    duplicates_handler.remove_duplicates()

                renamer = ImagesRenamer(images_dir=query_dir, new_name=query)
                renamer.rename_images()
