from typing import Literal, TypedDict

BingType = Literal[
    "photo",
    "clipart",
    "linedrawing",
    "transparent",
    "animated"
]
BingColor = Literal[
    "color",
    "blackandwhite",
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
    "brown",
]
BingSize = Literal[
    "extralarge",
    "large",
    "medium",
    "small"
]
BingLicense = Literal[
    "creativecommons",
    "publicdomain",
    "noncommercial",
    "commercial",
    "noncommercial,modify",
    "commercial,modify",
]
BingLayout = Literal[
    "square",
    "wide",
    "tall"
]
BingPeople = Literal[
    "face",
    "portrait"
]
BingDate = Literal[
    "pastday",
    "pastweek",
    "pastmonth",
    "pastyear"
]

class BingFiltersSpec(TypedDict, total=False):
    type: BingType
    color: BingColor
    size: BingSize | str
    license: BingLicense
    layout: BingLayout
    date: BingDate
