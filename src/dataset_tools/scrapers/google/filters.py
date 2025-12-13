from typing import Literal, TypedDict

from ..base.filters import DateRange

GoogleTypes = Literal[
    "photo",
    "face",
    "clipart",
    "linedrawing",
    "animated"
]
GoogleColor = Literal[
    "color",
    "blackandwhite",
    "transparent",
    "red",
    "orange",
    "yellow",
    "green",
    "teal",
    "blue",
    "purple",
    "pink",
    "white",
    "gray",
    "black",
    "brown"
]
GoogleSize = Literal[
    "large",
    "medium",
    "icon"
]
GoogleLicense = Literal[
    "noncommercial",
    "commercial",
    "noncommercial,modify",
    "commercial,modify"
]
GoogleDate = Literal[
    "anytime",
    "pastday",
    "pastweek",
    "pastmonth",
    "pastyear"
]

class GoogleFiltersSpec(TypedDict, total=False):
    type: GoogleTypes
    color: GoogleColor
    size: GoogleSize | str
    license: GoogleLicense
    date: GoogleDate | DateRange
