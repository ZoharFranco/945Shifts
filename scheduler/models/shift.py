from enum import Enum
from typing import Optional

from pydantic import BaseModel

from scheduler.models import Person
from scheduler.models.date_range import DateRange


class ShiftType(Enum):
    WORKDAY = 'workday'
    WEEKEND = 'weekend'
    HOLIDAY = 'holiday'


class Shift(BaseModel):
    person: Optional[Person]
    backup_person: Optional[Person]
    dates: DateRange
    type: ShiftType
    title: str
