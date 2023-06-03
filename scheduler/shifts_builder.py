from datetime import date, timedelta
from typing import Optional

from .holidays import get_holiday_name
from .models import Shift, ShiftType, DateRange

WEEKEND_DAYS = [3, 4, 5]
TITLE_PREFIX = '[947shift]'


class ShiftsBuilder:
    _start_date: date
    _end_date: date

    def __init__(self, start_date: date, end_date: date):
        self._start_date = start_date
        self._end_date = end_date

    @staticmethod
    def _is_night_before_holiday(_date: date) -> bool:
        next_day = _date + timedelta(days=1)
        current_holiday, next_day_holiday = [get_holiday_name(d) for d in (_date, next_day)]
        return next_day_holiday and current_holiday != next_day_holiday

    def _get_holiday_name(self, _date: date) -> Optional[str]:
        if self._is_night_before_holiday(_date):
            _date = _date + timedelta(days=1)

        holiday_name = get_holiday_name(_date)
        if holiday_name:
            return holiday_name

    @staticmethod
    def _is_weekend(_date: date) -> bool:
        return _date.weekday() in WEEKEND_DAYS

    def _build_holiday_shift(self, start_date: date) -> Shift:
        holiday_name = self._get_holiday_name(start_date)
        end_date = start_date + timedelta(days=1)

        while self._get_holiday_name(end_date) and not self._is_night_before_holiday(end_date):
            end_date += timedelta(days=1)

        end_date -= timedelta(days=1)
        return Shift(
            dates=DateRange(start=start_date, end=end_date),
            type=ShiftType.HOLIDAY,
            title=f'{TITLE_PREFIX} Holiday shift - {holiday_name}'
        )

    def _build_weekend_days_shift(self, start_date: date):
        end_date = start_date

        while self._is_weekend(end_date):
            end_date += timedelta(days=1)

        end_date -= timedelta(days=1)
        return Shift(
            dates=DateRange(start=start_date, end=end_date),
            type=ShiftType.WEEKEND,
            title=f'{TITLE_PREFIX} Weekend shift'
        )

    @staticmethod
    def _build_workday_shift(start_date: date):
        return Shift(
            dates=DateRange(start=start_date, end=start_date),
            type=ShiftType.WORKDAY,
            title=f'{TITLE_PREFIX} Workday shift'
        )

    def build(self) -> list[Shift]:
        shifts = list()
        current_date = self._start_date

        while current_date <= self._end_date:
            if self._get_holiday_name(current_date):
                shift = self._build_holiday_shift(current_date)
            elif self._is_weekend(current_date):
                shift = self._build_weekend_days_shift(current_date)
            else:
                shift = self._build_workday_shift(current_date)

            shifts.append(shift)
            current_date = shift.dates.end + timedelta(days=1)

        return shifts
