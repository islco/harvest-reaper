from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_calendar_events(token):
    creds = Credentials(token=token.token, refresh_token=token.token_secret)
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow().isoformat() + 'Z'
    # TODO: Add the strptime work
    # strptime_time_util = "%Y-%m-%dT%H:%M:%S%z"

    massaged_events = []
    try:
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
    except Exception as e:
        print(e)
        return massaged_events

    events = events_result.get('items', [])
    for event in events:
        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        massaged_events.append({
            "start": start,
            "end": end,
            "allDay": bool(not start and not end),
            "summary": event['summary']
        })

    return massaged_events
