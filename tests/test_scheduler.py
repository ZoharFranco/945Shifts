import json
from datetime import date
from pathlib import Path
import pandas as pd
from tempfile import NamedTemporaryFile, TemporaryFile
import pytest
from pydantic import parse_obj_as

from scheduler.justice_table import JusticeTable
from scheduler.models import Person, ShiftType
from scheduler.scheduler import Scheduler
from uuid import uuid4

PEOPLE_JSON_PATH = Path(__file__).parent / 'people.json'


@pytest.fixture
def scheduler() -> Scheduler:
    people = parse_obj_as(list[Person], json.loads(PEOPLE_JSON_PATH.read_text()))
    justice_table = JusticeTable(list())

    return Scheduler(
        start_date=date(2023, 3, 1),
        end_date=date(2023, 5, 1),
        people_pool=people,
        justice_table=justice_table,
        previous_schedule=list())


def tests_sanity(scheduler: Scheduler) -> None:
    scheduler.schedule()


def test_shifts_contain_people(scheduler: Scheduler) -> None:
    for shift in scheduler.schedule().shifts:
        assert shift.person


def test_custom_dates(scheduler: Scheduler) -> None:
    custom_holiday_name = 'Yom Haatzmaut'
    custom_holiday_shift = None

    for shift in scheduler.schedule().shifts:
        if custom_holiday_name in shift.title:
            custom_holiday_shift = shift

    assert custom_holiday_shift
    assert custom_holiday_shift.dates.start == date(2023, 4, 25)
    assert custom_holiday_shift.dates.end == date(2023, 4, 26)
    assert custom_holiday_shift.type == ShiftType.HOLIDAY


def test_csv_schedule(scheduler: Scheduler) -> None:
    schedule = scheduler.schedule()

    output_path = Path(__file__).parent / f'{uuid4().hex}.csv'
    schedule.save_to_csv_file(output_path)
    pd.read_csv(output_path)
    output_path.unlink()
