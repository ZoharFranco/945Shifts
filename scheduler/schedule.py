from __future__ import annotations

import json
from pathlib import Path
from typing import Union

import pandas as pd
from pydantic import parse_obj_as
from pydantic.json import pydantic_encoder

from scheduler.google_api_client import GoogleAPIClient
from scheduler.models import Shift


class Schedule:
    _shifts: list[Shift]
    _google_api_client: GoogleAPIClient

    def __init__(self, shifts: list[Shift]):
        self._shifts = shifts
        self._google_api_client = GoogleAPIClient()

    @staticmethod
    def from_json_file(file_path: Union[str, Path]) -> Schedule:
        shifts = parse_obj_as(list[Shift], json.loads(Path(file_path).read_text()))
        return Schedule(shifts)

    @property
    def _json_shifts(self) -> str:
        return json.dumps(self._shifts, default=pydantic_encoder)

    def save_to_json_file(self, file_path: Union[str, Path]) -> None:
        Path(file_path).write_text(self._json_shifts)

    def save_to_csv_file(self, file_path: Union[str, Path]):
        df = pd.read_json(self._json_shifts)

        for column in ['person', 'backup_person']:
            df[column] = df[column].map(lambda p: p['full_name'])

        df['start_date'] = df['dates'].map(lambda d: d['start'])
        df['end_date'] = df['dates'].map(lambda d: d['end'])
        df.pop('dates')

        df.to_csv(file_path)

    @property
    def shifts(self) -> list[Shift]:
        return self._shifts

    def send_appointments(self):
        for shift in self._shifts:
            self._google_api_client.schedule_appointment(
                title=shift.title,
                start_date=shift.dates.start,
                end_date=shift.dates.end,
                target_email=shift.person.email_address
            )

            self._google_api_client.schedule_appointment(
                title=f'{shift.title} - REZERVA',
                start_date=shift.dates.start,
                end_date=shift.dates.end,
                target_email=shift.backup_person.email_address
            )
