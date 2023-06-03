from __future__ import annotations

from pydantic import BaseModel

from scheduler.models import Person, ShiftType

SHIFT_TYPE_TO_FIELD_MAPPING = {
    ShiftType.WEEKEND: 'weekend_days_debt',
    ShiftType.WORKDAY: 'workdays_debt',
    ShiftType.HOLIDAY: 'holidays_debt'
}


class JusticeRecord(BaseModel):
    person: Person

    # For example - if a person1 takes shift from person2, person1 has a dept of -1, and person2 has debt of 1.
    workdays_debt: float
    weekend_days_debt: float
    holidays_debt: float

    @staticmethod
    def get_default(person: Person) -> JusticeRecord:
        return JusticeRecord(
            person=person,
            workdays_debt=0,
            weekend_days_debt=0,
            holidays_debt=0,
        )

    def get_debt(self, shift_type: ShiftType) -> float:
        return self.dict()[SHIFT_TYPE_TO_FIELD_MAPPING[shift_type]]

    def add_debt(self, shift_type: ShiftType, value: float) -> None:
        setattr(self, SHIFT_TYPE_TO_FIELD_MAPPING[shift_type], self.get_debt(shift_type) + value)

    def substract_debt(self, shift_type: ShiftType, value: float) -> None:
        self.add_debt(shift_type, -value)
