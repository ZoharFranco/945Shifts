from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional
from pyluach import dates


@dataclass
class Date:
    day: int
    month: int

    def to_hebrew_date(self, hebrew_year: int) -> dates.HebrewDate:
        return dates.HebrewDate(hebrew_year, self.month, self.day)

    def to_gregorian_date(self, gregorian_year: int) -> dates.GregorianDate:
        return dates.GregorianDate(gregorian_year, self.month, self.day)


@dataclass
class HolidaysDateRange:
    start: Date
    end: Date


@dataclass
class CustomHoliday(ABC):
    name: str
    date_range: HolidaysDateRange

    @abstractmethod
    def contains(self, _date: dates.BaseDate) -> bool:
        pass


class CustomHebrewHoliday(CustomHoliday):
    def contains(self, _date: dates.GregorianDate) -> bool:
        start = self.date_range.start.to_hebrew_date(_date.to_heb().year)
        end = self.date_range.end.to_hebrew_date(_date.to_heb().year)
        return start <= _date <= end


class CustomForeignHoliday(CustomHoliday):
    def contains(self, _date: dates.GregorianDate) -> bool:
        start = self.date_range.start.to_hebrew_date(_date.year)
        end = self.date_range.end.to_hebrew_date(_date.year)
        return start <= _date <= end


class HebrewMonth(Enum):
    NISSAN = 1
    IYAR = 2
    SIVAN = 3
    TAMUZ = 4
    AV = 5
    ELUL = 6
    TISHREI = 7
    HESHVAN = 8
    KISLEV = 9
    TEVET = 10
    SHVAT = 11
    ADAR_A = 12
    ADAR_B = 13


# List of all holidays that does not appear in pyluach
CUSTOM_HOLIDAYS = [
    CustomHebrewHoliday(
        name='Yom Haatzmaut',
        date_range=HolidaysDateRange(
            Date(day=5, month=HebrewMonth.IYAR.value),
            Date(day=5, month=HebrewMonth.IYAR.value))
    ),
    CustomForeignHoliday(name='Silvester', date_range=HolidaysDateRange(
        Date(day=1, month=1),
        Date(day=1, month=1)))
]

# Holidays that should be ignored
IGNORED_HOLIDAYS = [
    CustomHebrewHoliday(name='Pesach Hol Hamoed', date_range=HolidaysDateRange(
        Date(day=16, month=HebrewMonth.NISSAN.value),
        Date(day=20, month=HebrewMonth.NISSAN.value)
    )),
    CustomHebrewHoliday(name='Pesach Sheni', date_range=HolidaysDateRange(
        Date(day=14, month=HebrewMonth.IYAR.value),
        Date(day=20, month=HebrewMonth.IYAR.value)
    )),
]


def _get_custom_holiday_name(_date: dates.GregorianDate) -> Optional[str]:
    for holiday in CUSTOM_HOLIDAYS:
        if holiday.contains(_date):
            return holiday.name


def get_holiday_name(_date: date) -> Optional[str]:
    pyluach_date = dates.GregorianDate(_date.year, _date.month, _date.day)
    if any(holiday.contains(pyluach_date) for holiday in IGNORED_HOLIDAYS):
        return None

    holiday_name = pyluach_date.holiday()
    if not holiday_name:
        holiday_name = _get_custom_holiday_name(pyluach_date)

    return holiday_name
