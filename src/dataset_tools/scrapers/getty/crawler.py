from icrawler import Crawler

from .feeder import GettyImagesFeeder
from .parser import GettyImagesParser
from .downloader import GettyImagesDownloader


class GettyImagesCrawler(Crawler):

    def __init__(
        self,
        feeder_cls=GettyImagesFeeder,
        parser_cls=GettyImagesParser,
        downloader_cls=GettyImagesDownloader,
        *args,
        **kwargs
    ):
        super().__init__(feeder_cls, parser_cls, downloader_cls, *args, **kwargs)

    def crawl(
        self,
        keyword: str,
        filters: dict[str, str] | None = None,
        offset: int = 0,
        max_num: int = 100,
        min_size: int | None = None,
        max_size: int | None = None,
        file_idx_offset: int = 0,
        overwrite: bool = False,
        max_idle_time: int = None,
    ):
        feeder_kwargs = dict(
            keyword=keyword,
            offset=offset,
            max_num=max_num,
            filters=filters
        )
        downloader_kwargs = dict(
            max_num=max_num,
            min_size=min_size,
            max_size=max_size,
            file_idx_offset=file_idx_offset,
            overwrite=overwrite,
            max_idle_time=max_idle_time,
        )
        super().crawl(
            feeder_kwargs=feeder_kwargs,
            downloader_kwargs=downloader_kwargs
        )
