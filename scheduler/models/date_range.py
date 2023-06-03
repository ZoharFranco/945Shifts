from __future__ import annotations
from datetime import date
from typing import Union

from pydantic import BaseModel


class DateRange(BaseModel):
    start: date
    end: date

    def contains_date(self, _date: date) -> bool:
        return self.start <= _date <= self.end

    @property
    def total_days(self) -> int:
        return (self.end - self.start).days + 1

    def overlaps_with(self, other: Union[DateRange, date]) -> bool:
        if isinstance(other, date):
            return self.contains_date(other)
        else:
            return other.contains_date(self.start) or other.contains_date(self.end) or self.contains_date(
                other.start) or self.contains_date(other.end)

    def __repr__(self):
        return f'{self.start} {self.end}'
