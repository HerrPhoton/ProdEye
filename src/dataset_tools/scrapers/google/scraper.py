from typing import Literal
from pathlib import Path

from icrawler.builtin import GoogleImageCrawler

from ..base import Scraper
from .filters import GoogleFiltersSpec
from .storage import GoogleStorage
from ....utils import PathLike
from ..base.downloader import PrefixDownloader


class GoogleScraper(Scraper):

    def scrape(
        self,
        query: str,
        output_dir: PathLike,
        filters: GoogleFiltersSpec | None = None,
        offset: int = 0,
        max_num: int | None = 100,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        file_idx_offset: int | Literal["auto"] = "auto",
        overwrite: bool = False,
        max_idle_time: int | None = None,
        language: str | None = None
    ) -> None:
        """
        Скачивает изображения с Google по заданному поисковому запросу.

        Скачанные изображения будут иметь префикс ``google_`` и индекс изображения.

        :param query: Поисковый запрос для Google.
        :type query: str
        :param output_dir: Директория для сохранения изображений.
        :type output_dir: PathLike
        :param filters: Фильтры поиска в Google.
        :type filters: GoogleFiltersSpec | None, optional
        :param offset: Номер стартового изображения с начала списка результатов.
        :type offset: int, optional
        :param max_num: Максимальное количество изображений для скачивания.
        :type max_num: int | None, optional
        :param min_size: Минимально допустимый размер изображения ``(ширина, высота)``.
        :type min_size: int | None, optional
        :param max_size: Максимально допустимый размер изображения ``(ширина, высота)``.
        :type max_size: int | None, optional
        :param file_idx_offset: Начальный индекс для формирования имён файлов изображений.
            При ``"auto"`` автоматически определяет начальный индекс.
        :type file_idx_offset: int | Literal["auto"], optional
        :param overwrite: Перезаписывать ли существующие файлы с одинаковыми именами.
        :type overwrite: bool, optional
        :param max_idle_time: Максимальное время ожидания (в секундах) появления новых изображений.
            При превышении этого времени загрузка прекращается.
        :type max_idle_time: int | None, optional
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        crawler = GoogleImageCrawler(
            downloader_cls=PrefixDownloader,
            feeder_threads=self.num_workers,
            parser_threads=self.num_workers,
            downloader_threads=self.num_workers,
            storage=GoogleStorage(str(output_dir)),
        )
        crawler.crawl(
            keyword=query,
            filters=filters,
            offset=offset,
            max_num=max_num,
            min_size=min_size,
            max_size=max_size,
            file_idx_offset=file_idx_offset,
            overwrite=overwrite,
            max_idle_time=max_idle_time,
            language=language
        )
