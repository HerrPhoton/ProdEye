import datetime

DateTuple = tuple[int, int, int]
DateRange = tuple[DateTuple | datetime.date, DateTuple | datetime.date]
