from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Union, Optional

from pydantic import parse_obj_as
from pydantic.json import pydantic_encoder

from .models import JusticeRecord, Person, ShiftType


class JusticeTable:
    _records: list[JusticeRecord]

    def __init__(self, records: Optional[list[JusticeRecord]] = None):
        self._records = records or list()

    @staticmethod
    def from_file(file_path: Union[str, Path]) -> JusticeTable:
        file_content = Path(file_path).read_text()
        records = parse_obj_as(list[JusticeRecord], json.loads(file_content))
        return JusticeTable(records)

    def save_to_file(self, file_path: Union[str, Path], people_whitelist: Optional[list[Person]] = None) -> None:
        records = self._records
        if people_whitelist:
            records = [record for record in records if record.person in people_whitelist]
        Path(file_path).write_text(json.dumps(records, default=pydantic_encoder))

    def get_person_record(self, person: Person) -> JusticeRecord:
        for record in self._records:
            if record.person == person:
                return record

        record = JusticeRecord.get_default(person)
        self._records.append(record)
        return record

    def get_shift_candidates(self, shift_type: ShiftType) -> list[Person]:
        """
        :return: Sorted list that starts with the best candidate to the worst.
        """
        candidates = list()
        candidate_groups = dict()

        for record in self._records:
            debt = record.get_debt(shift_type)
            if debt not in candidate_groups.keys():
                candidate_groups[debt] = [record.person]
            else:
                candidate_groups[debt].append(record.person)

        for debt in reversed(sorted(candidate_groups.keys())):
            candidate_group = candidate_groups[debt]
            random.shuffle(candidate_group)
            candidates.extend(candidate_group)

        return candidates

    def add_debts(self, workdays: int, weekend_days: int, holidays: int, people: list[Person]) -> None:
        workdays_availability = sum(person.workdays_shifts_weight for person in people)
        weekend_days_availability = sum(person.weekend_days_shifts_weight for person in people)
        holidays_availability = sum(person.holidays_shifts_weight for person in people)

        for person in people:
            record = self.get_person_record(person)
            record.workdays_debt += (workdays / workdays_availability) * person.workdays_shifts_weight
            record.weekend_days_debt += (weekend_days / weekend_days_availability) * person.weekend_days_shifts_weight
            record.holidays_debt += (holidays / holidays_availability) * person.holidays_shifts_weight
