import json
from datetime import date
import logging
from pathlib import Path

from pydantic import parse_obj_as

from scheduler.justice_table import JusticeTable
from scheduler.models import Person
from scheduler.schedule import Schedule
from scheduler.scheduler import Scheduler

_logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

BASE_PATH = Path(__file__).parent
PEOPLE_PATH = BASE_PATH / 'people.json'
JUSTICE_TABLE_PATH = BASE_PATH / 'justice_table.json'
PREVIOUS_SCHEDULE_PATH = BASE_PATH / 'previous_shifts.json'
CSV_OUTPUT_PATH = BASE_PATH / 'schedule.csv'

INTRO_ASCII_ART = r"""
 _________.__    .__  _____  __          
 /   _____/|  |__ |__|/ ____\/  |_  ______
 \_____  \ |  |  \|  \   __\\   __\/  ___/
 /        \|   Y  \  ||  |   |  |  \___ \ 
/_______  /|___|  /__||__|   |__| /____  >
        \/      \/                     \/ 
"""


def print_intro() -> None:
    print(INTRO_ASCII_ART)
    print('Welcome to shifts scheduler!')


def get_schedule_dates() -> tuple[date, date]:
    start_date = input('Please enter start date (Format: "YYYY-MM-DD"): ')
    end_date = input('Please enter end date (Format: "YYYY-MM-DD"): ')
    dates = list()
    for _date in [start_date, end_date]:
        dates.append([int(number) for number in _date.split('-')])
    start_date = date(*dates[0])
    end_date = date(*dates[1])
    return start_date, end_date


def get_people():
    _logger.info(f'Loading people from file: {PEOPLE_PATH}')
    people = parse_obj_as(list[Person], json.loads(PEOPLE_PATH.read_text()))
    return people


def get_scheduler(people: list[Person]) -> Scheduler:
    start_date, end_date = get_schedule_dates()
    if JUSTICE_TABLE_PATH.is_file():
        _logger.info(f'Loading justice table from file: {JUSTICE_TABLE_PATH}')
        justice_table = JusticeTable.from_file(JUSTICE_TABLE_PATH)
    else:
        _logger.info('Justice table does not exist, creating an empty justice table.')
        justice_table = JusticeTable()

    previous_schedule = None
    if PREVIOUS_SCHEDULE_PATH.is_file():
        _logger.info(f'Loading previous shifts from file: {PREVIOUS_SCHEDULE_PATH}')
        previous_schedule = Schedule.from_json_file(PREVIOUS_SCHEDULE_PATH)

    return Scheduler(start_date, end_date, people, justice_table, previous_schedule=previous_schedule)


def ask_for_confirmation(prompt: str) -> bool:
    answer = input(f'{prompt} | Do you agree (Y/N): ')
    return answer.lower().strip() == 'y'


def main() -> None:
    print_intro()
    people = get_people()
    scheduler = get_scheduler(people)
    schedule = scheduler.schedule()
    schedule.save_to_csv_file(CSV_OUTPUT_PATH)

    if not ask_for_confirmation(f'Wrote schedule to "{CSV_OUTPUT_PATH}"'):
        return

    _logger.info(f'Saving justice table to: "{JUSTICE_TABLE_PATH}"')
    scheduler.justice_table.save_to_file(JUSTICE_TABLE_PATH, people_whitelist=people)

    if ask_for_confirmation('I\'m about to send calendar appointments to all the people'):
        schedule.send_appointments()


if __name__ == '__main__':
    main()
