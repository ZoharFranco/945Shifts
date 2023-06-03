from datetime import date
from typing import Union

from pydantic import BaseModel, Field

from scheduler.models.date_range import DateRange


class Person(BaseModel):
    full_name: str
    email_address: str
    workdays_shifts_weight: float
    weekend_days_shifts_weight: float
    holidays_shifts_weight: float

    # days in which the person cannot do the shift
    constraints: list[Union[DateRange, date]] = Field(default_factory=list)

    def __hash__(self) -> int:
        return hash(f'{self.full_name}.{self.email_address}')

    def __eq__(self, other) -> bool:
        return hash(self) == hash(other)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return self.__str__()
