import sys
from datetime import date
from logging import getLogger
from typing import Optional

from .justice_table import JusticeTable
from .models import Shift, ShiftType
from .models.person import Person
from .schedule import Schedule
from .shifts_builder import ShiftsBuilder

SPACE_BETWEEN_SHIFT_TYPES_MAPPING = {
    ShiftType.WEEKEND: 2,
    ShiftType.WORKDAY: 5,
    ShiftType.HOLIDAY: 0
}

MIN_SPACE_BETWEEN_ALL_SHIFT_TYPES = 2

_logger = getLogger(__name__)


class Scheduler:
    _start_data: date
    _end_date: date
    _people_pool: list[Person]
    _justice_table: JusticeTable
    _shifts = list[Shift]
    _previous_shifts = list[Shift]

    def __init__(self, start_date: date, end_date: date, people_pool: list[Person], justice_table: JusticeTable,
                 previous_schedule: Optional[Schedule] = None):
        self._start_data = start_date
        self._end_date = end_date
        self._people_pool = people_pool
        self._justice_table = justice_table
        self._shifts = ShiftsBuilder(start_date, end_date).build()
        self._previous_shifts = previous_schedule.shifts if previous_schedule else list()

    @property
    def justice_table(self) -> JusticeTable:
        return self._justice_table

    def _get_space_from_last_shift(self, person: Person, shift: Shift, any_type: bool = False) -> int:
        all_shifts = [*self._previous_shifts, *self._shifts]
        relevant_shifts = all_shifts[:all_shifts.index(shift)]
        any_previous_shift = False
        space = 0

        for current_shift in reversed(relevant_shifts):
            if any_type or current_shift.type == shift.type:
                if current_shift.person != person and current_shift.backup_person != person:
                    space += 1
                else:
                    any_previous_shift = True
                    break

        if not any_previous_shift:
            return sys.maxsize

        return space

    def _is_compatible_for_shift(self, person: Person, shift: Shift) -> bool:
        has_constraint = any(shift.dates.overlaps_with(constraint) for constraint in person.constraints)
        if has_constraint:
            _logger.debug(f'{person.full_name} has constraints on shift: {shift.dates}')
            return False

        min_shift_space = SPACE_BETWEEN_SHIFT_TYPES_MAPPING[shift.type]
        space_from_last_shift = self._get_space_from_last_shift(person, shift)
        if space_from_last_shift < min_shift_space:
            _logger.debug(f'{person} space from last {shift.type} shift is too '
                          f'small ({space_from_last_shift}): {shift.dates}')
            return False

        space_from_last_shift = self._get_space_from_last_shift(person, shift, any_type=True)
        if self._get_space_from_last_shift(person, shift, any_type=True) < MIN_SPACE_BETWEEN_ALL_SHIFT_TYPES:
            _logger.debug(f'{person} space from last shift is too small {space_from_last_shift}')
            return False

        return True

    def _choose_person_for_shift(self, shift: Shift) -> None:
        candidates = list()
        for candidate in self._justice_table.get_shift_candidates(shift.type):
            if self._is_compatible_for_shift(candidate, shift):
                candidates.append(candidate)

        chosen_person = candidates[0]
        chosen_backup_person = candidates[1]

        chosen_person_record = self._justice_table.get_person_record(chosen_person)
        chosen_person_record.substract_debt(shift.type, shift.dates.total_days)

        shift.person = chosen_person
        shift.backup_person = chosen_backup_person

    def _get_total_days(self, shift_type: ShiftType):
        return sum(shift.dates.total_days for shift in self._shifts if shift.type == shift_type)

    def schedule(self) -> Schedule:
        self._justice_table.add_debts(
            workdays=self._get_total_days(ShiftType.WORKDAY),
            weekend_days=self._get_total_days(ShiftType.WEEKEND),
            holidays=self._get_total_days(ShiftType.HOLIDAY),
            people=self._people_pool
        )

        for shift in self._shifts:
            self._choose_person_for_shift(shift)

        return Schedule(self._shifts)
