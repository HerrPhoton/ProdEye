from abc import ABC, abstractmethod
from typing import Any, Literal
from pathlib import Path
from collections.abc import Mapping, Sequence

from ....utils import PathLike


class Scraper(ABC):

    def __init__(self, num_workers: int = 1):
        """Инициализация скраппера изображений.

        :param int num_workers:
            Количество рабочих потоков/процессов для загрузки изображений
        """
        self.num_workers = num_workers

    @abstractmethod
    def scrape(
        self,
        query: str,
        output_dir: PathLike,
        filters: Mapping[str, Any] | None = None,
        offset: int = 0,
        max_num: int | None = 100,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        file_idx_offset: int | Literal["auto"] = "auto",
        overwrite: bool = False,
        max_idle_time: int | None = None,
    ) -> None:
        """Скачивает изображения по заданному поисковому запросу.

        :param str query:
            Поисковый запрос.

        :param PathLike output_dir:
            Директория для сохранения скачанных изображений.

        :param Mapping[str, Any] | None filters:
            Набор фильтров, применяемых к поисковой выдаче.
            Поддерживаемые ключи и типы значений зависят от конкретной реализации Scraper.

        :param int offset:
            Смещение начала выборки результатов.
            Семантика параметра определяется конкретным скраппером

        :param int | None max_num:
            Максимальное количество изображений для скачивания.

        :param int | None min_size:
            Минимально допустимый размер изображения (ширина, высота).

        :param int | None max_size:
            Максимально допустимый размер изображения (ширина, высота).

         :param int | Literal["auto"] file_idx_offset:
            Начальный индекс для формирования имён файлов изображений.
            При "auto" автоматически определяет начальный индекс.

        :param bool overwrite:
            Перезаписывать ли существующие файлы с одинаковыми именами.

        :param int | None max_idle_time:
            Максимальное время ожидания (в секундах) появления новых изображений.
            При превышении этого времени загрузка прекращается.
        """
        raise NotImplementedError

    def scrape_many(
        self,
        queries: Sequence[str],
        output_dir: PathLike,
        filters: Mapping[str, Any] | None = None,
        offset: int = 0,
        max_num: int | None = 100,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        file_idx_offset: int | Literal["auto"] = "auto",
        overwrite: bool = False,
        max_idle_time: int | None = None,
    ) -> None:
        """Скачивает изображения для набора поисковых запросов.

        Для каждого запроса создаётся отдельная поддиректория внутри `output_dir`.

        :param Sequence[str] queries:
            Набор поисковых запросов.

        :param PathLike output_dir:
            Корневая директория для сохранения изображений.

        :param Mapping[str, Any] | None filters:
            Набор фильтров, применяемых к поисковой выдаче.
            Поддерживаемые ключи и типы значений зависят от конкретной реализации Scraper.

        :param int offset:
            Смещение начала выборки результатов.
            Семантика параметра определяется конкретным скраппером

        :param int | None max_num:
            Максимальное количество изображений для скачивания.

        :param int | None min_size:
            Минимально допустимый размер изображения (ширина, высота).

        :param int | None max_size:
            Максимально допустимый размер изображения (ширина, высота).

        :param int | Literal["auto"] file_idx_offset:
            Начальный индекс для формирования имён файлов изображений.
            При "auto" автоматически определяет начальный индекс.

        :param bool overwrite:
            Перезаписывать ли существующие файлы с одинаковыми именами.

        :param int | None max_idle_time:
            Максимальное время ожидания (в секундах) появления новых изображений.
            При превышении этого времени загрузка прекращается.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for query in queries:
            # Создание поддиректории с названием запроса
            query_dir = output_dir / query.replace(" ", "_")
            query_dir.mkdir(exist_ok=True)

            self.scrape(
                query=query,
                output_dir=query_dir,
                filters=filters,
                offset=offset,
                max_num=max_num,
                min_size=min_size,
                max_size=max_size,
                file_idx_offset=file_idx_offset,
                overwrite=overwrite,
                max_idle_time=max_idle_time
            )
