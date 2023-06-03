import datetime
from logging import getLogger
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

_logger = getLogger(__name__)
CREDENTIALS_FILE_PATH = Path(__file__).parent / 'credentials.json'
TOKEN_JSON_PATH = Path(__file__).parent / 'token.json'
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.profile']


class GoogleAPIClient:
    _credentials: Credentials

    def __init__(self):
        self._credentials = self.get_credentials()

    @staticmethod
    def get_credentials() -> Credentials:
        credentials = None

        if TOKEN_JSON_PATH.exists():
            credentials = Credentials.from_authorized_user_file(TOKEN_JSON_PATH, SCOPES)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE_PATH, SCOPES)
                credentials = flow.run_local_server(port=0)
            TOKEN_JSON_PATH.write_text(credentials.to_json())

        return credentials

    def schedule_appointment(self, title: str, start_date: datetime.date, end_date: datetime.date,
                             target_email: str) -> None:
        """
        Schedule an appointment on Google Calendar API.
        :param title: The title of the appointment.
        :param start_date: The start date of the appointment (as a date object).
        :param end_date: The end date of the appointment (as a date object).
        :param target_email: The email address of the person to invite to the appointment.
        """
        service = build('calendar', 'v3', credentials=self._credentials)
        event = {
            'summary': title,
            'start': {
                'date': start_date.isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'date': (end_date + datetime.timedelta(days=1)).isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'attendees': [{'email': target_email}],
            'reminders': {
                'useDefault': True,
            }
        }
        try:
            service.events().insert(calendarId='primary', body=event).execute()
        except HttpError as error:
            _logger.exception(error)
            _logger.error('Encountered an error while scheduling an appointment')
