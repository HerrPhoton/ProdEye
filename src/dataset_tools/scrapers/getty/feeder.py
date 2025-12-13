from typing import get_args
from urllib.parse import parse_qsl, urlencode

from icrawler import Feeder
from icrawler.builtin import Filter

from .filters import GettySort, GettyImagesFilters, GettyImagesFiltersSpec


class GettyImagesFeeder(Feeder):

    FILTER_REGISTRY = {
        "sort": {
            "format_fn": GettyImagesFilters.sort,
            "choices": list(get_args(GettySort)),
        },
        "date": {
            "format_fn": GettyImagesFilters.date,
        },
        "license": {
            "format_fn": GettyImagesFilters.license,
        },
        "orientation": {
            "format_fn": GettyImagesFilters.orientation,
        },
        "style": {
            "format_fn": GettyImagesFilters.style,
        },
    }
    BASE_URL = "https://www.gettyimages.com/search/2/image"

    def get_filter(self):
        search_filter = Filter()

        for name, params in self.FILTER_REGISTRY.items():
            search_filter.add_rule(
                name=name,
                format_fn=params["format_fn"],
                choices=params.get("choices")
            )
        return search_filter

    def feed(self, keyword: str, offset: int, max_num: int, filters: GettyImagesFiltersSpec | None = None):
        self.filter = self.get_filter()
        filter_str = self.filter.apply(filters, sep="&")

        for page in range(offset + 1, 101):
            params = dict(phrase=keyword, page=page)
            params.update(dict(parse_qsl(filter_str)))

            url = f"{self.BASE_URL}?{urlencode(params)}"
            self.out_queue.put(url)
