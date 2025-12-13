import datetime
from typing import Literal, TypedDict, get_args
from collections.abc import Iterable

from ..base.filters import DateRange

GettySort = Literal[
    "most popular",
    "best",
    "newest",
    "oldest",
]
GettyDateLiteral = Literal[
    "last 24 hours",
    "last 48 hours",
    "last 72 hours",
    "last 7 days",
    "last 30 days",
    "last 12 months",
]
GettyDate = GettyDateLiteral | DateRange

GettyLicense = Literal[
    "royalty-free",
    "rights-managed",
]
GettyOrientation = Literal[
    "vertical",
    "horizontal",
    "square",
    "panoramic horizontal",
    "panoramic vertical",
]
GettyStyle = Literal[
    "abstract",
    "portrait",
    "close-up",
    "sparse",
    "cut out",
    "full frame",
    "copy space",
    "macro",
    "still life",
]

class GettyImagesFiltersSpec(TypedDict, total=False):
    sort: GettySort
    date: GettyDate
    license: GettyLicense | Iterable[GettyLicense]
    orientation: GettyOrientation | Iterable[GettyOrientation]
    style: GettyStyle | Iterable[GettyStyle]


class GettyImagesFilters:

    @staticmethod
    def normalize(value: str) -> str:
        return (
            value
            .replace(" ", "")
            .replace("-", "")
            .lower()
        )

    @classmethod
    def sort(cls, value: GettySort) -> str:
        allowed = get_args(GettySort)

        key = cls._validate_literal(
            value=value,
            allowed=allowed,
            error_msg=(
                'filter option "sort" must be one of: '
                f'{", ".join(allowed)}'
            ),
        )
        return f"sort={key}"

    @classmethod
    def date(cls, value: GettyDate) -> str:

        allowed = get_args(GettyDateLiteral)

        try:
            # Предопределенные периоды
            if isinstance(value, str):
                key = cls._validate_literal(
                    value=value,
                    allowed=allowed
                )
                return f"recency={key}"

            # Диапазон дат
            if isinstance(value, tuple) and len(value) == 2:
                start, end = value
                begin_date = cls._to_iso(start)
                end_date = cls._to_iso(end)
                return f"begindate={begin_date}&enddate={end_date}"

            raise TypeError

        except TypeError:
            raise TypeError(
                'filter option "date" must be one of: '
                f'{", ".join(allowed)} or a tuple of two dates'
            )

    @classmethod
    def license(cls, values: GettyLicense | Iterable[GettyLicense]) -> str:

        LICENSES_MAP = {
            "royaltyfree": "rf",
            "rightsmanaged": "rm",
        }

        if isinstance(values, str):
            values = [values]

        allowed = get_args(GettyLicense)

        formatted = []
        for v in values:
            key = cls._validate_literal(
                value=v,
                allowed=allowed,
                error_msg=(
                    'filter option "license" one or more of: '
                    f'{", ".join(allowed)}'
                )
            )
            formatted.append(LICENSES_MAP[key])

        return "license=" + ",".join(formatted)

    @classmethod
    def orientation(cls, values: GettyOrientation | Iterable[GettyOrientation]) -> str:

        if isinstance(values, str):
            values = [values]

        allowed = get_args(GettyOrientation)

        formatted = []
        for v in values:
            key = cls._validate_literal(
                value=v,
                allowed=allowed,
                error_msg=(
                    'filter option "orientation" be one or more of: '
                    f'{", ".join(allowed)}'
                )
            )
            formatted.append(key)

        return "orientations=" + ",".join(formatted)

    @classmethod
    def style(cls, values: str | Iterable[str]) -> str:

        if isinstance(values, str):
            values = [values]

        allowed = get_args(GettyStyle)

        formatted = []
        for v in values:
            key = cls._validate_literal(
                value=v,
                allowed=allowed,
                error_msg=(
                    'filter option "style" must be one or more of: '
                    f'{", ".join(allowed)}'
                )
            )
            formatted.append(key)

        return "compositions=" + ",".join(formatted)

    @classmethod
    def _to_iso(cls, d: datetime.date | tuple[int, int, int]) -> str:
        if isinstance(d, tuple):
            d = datetime.date(*d)

        if not isinstance(d, datetime.date):
            raise TypeError

        return d.strftime("%Y-%m-%d")

    @classmethod
    def _validate_literal(
        cls,
        value: str,
        allowed: Iterable[str],
        error_msg: str | None = None,
    ) -> str:

        # Нормализация допустимых значений
        normalized_allowed = {
            cls.normalize(v): v for v in allowed
        }

        # Нормализация указанного значения
        key = cls.normalize(value)
        if key not in normalized_allowed:
            raise TypeError(error_msg)

        return key
