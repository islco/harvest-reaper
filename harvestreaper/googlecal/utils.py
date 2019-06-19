from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_calendar_events(token, start_date, end_date):
    creds = Credentials(token=token.token, refresh_token=token.token_secret)
    service = build('calendar', 'v3', credentials=creds)
    formatted_start = start_date.isoformat() + 'Z'
    formatted_end = end_date.isoformat() + 'Z'
    strptime_time_util = "%Y-%m-%dT%H:%M:%S%z"
    strftime_time_util = "%I:%M%p"

    massaged_events = []
    try:
        events_result = service.events().list(calendarId='primary', timeMin=formatted_start,
                                              timeMax=formatted_end, singleEvents=True,
                                              orderBy='startTime').execute()
    except Exception as e:
        print(e)
        return massaged_events

    events = events_result.get('items', [])
    for event in events:
        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        day_of_week = None
        massaged_start = "09:00"
        massaged_end = "05:00"
        duration = 8 * 60 * 60
        for attendee in event.get('attendees', []):
            if attendee.get('self', '') is True and attendee.get('responseStatus', '') == 'declined':  # noqa
                continue

        if start and end:
            start_obj = datetime.strptime(start, strptime_time_util)
            end_obj = datetime.strptime(end, strptime_time_util)

            day_of_week = start_obj.strftime('%a')
            duration = (end_obj - start_obj).total_seconds()
            massaged_start = start_obj.strftime(strftime_time_util)
            massaged_end = end_obj.strftime(strftime_time_util)
        else:
            day_of_week = datetime.strptime(event['start'].get('date'), '%Y-%m-%d').strftime('%a')
            massaged_start = "09:00AM"
            massaged_end = "05:00PM"

        massaged_events.append({
            "start": massaged_start,
            "end": massaged_end,
            "day_of_week": day_of_week,
            "duration": round(duration / 60 / 60, 2),
            "summary": event['summary']
        })

    return massaged_events
