from datetime import datetime, timedelta
from pytz import timezone, UTC

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from harvestreaper.googlecal.views import GoogleOAuth2Adapter
from harvestreaper.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

STRPTIME_UTIL = "%Y-%m-%dT%H:%M:%S%z"
STRFTIME_UTIL = "%I:%M %p"


def _get_creds(token):
    now = UTC.localize(datetime.now())
    creds = Credentials(token=token.token, refresh_token=token.token_secret,
                        token_uri=GoogleOAuth2Adapter.access_token_url,
                        client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET)

    # Refresh the token if the token is expired
    if now > token.expires_at:
        try:
            creds.refresh(Request())
        except RefreshError:
            print('Error: User failed to have their token refreshed')
            return None
        token.token = creds.token
        token.token_secret = creds.refresh_token
        token.expires_at = UTC.localize(creds.expiry)
        token.save()

    return creds


def get_calendar_events(token, start_date, end_date):
    creds = _get_creds(token)
    if creds is None:
        return None
    service = build('calendar', 'v3', credentials=creds)
    formatted_start = start_date.isoformat() + 'Z'
    formatted_end = end_date.isoformat() + 'Z'

    massaged_events = {
        'Sat': [],
        'Sun': [],
        'Mon': [],
        'Tue': [],
        'Wed': [],
        'Thu': [],
        'Fri': []
    }
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
        declined_event = False
        massaged_start = "09:00"
        massaged_end = "05:00"
        duration = 8 * 60 * 60
        for attendee in event.get('attendees', []):
            if attendee.get('self', '') is True and attendee.get('responseStatus', '') == 'declined':  # noqa
                declined_event = True

        if declined_event:
            continue

        if start and end:
            start_obj = datetime.strptime(start, STRPTIME_UTIL)
            end_obj = datetime.strptime(end, STRPTIME_UTIL)

            day_of_week = start_obj.strftime('%a')
            duration = (end_obj - start_obj).total_seconds()
            massaged_start = start_obj.strftime(STRFTIME_UTIL)
            massaged_end = end_obj.strftime(STRFTIME_UTIL)
        else:
            raw_day = timezone(
                'US/Eastern').localize(datetime.strptime(event['start'].get('date'), '%Y-%m-%d'))
            day_of_week = raw_day.strftime('%a')
            start = datetime.strftime(raw_day + timedelta(hours=9),
                                      STRPTIME_UTIL)  # Set to 9AM by default
            massaged_start = "09:00 AM"
            massaged_end = "05:00 PM"

        massaged_events[day_of_week].append({
            "start": massaged_start,
            "raw_start": start,
            "end": massaged_end,
            "duration": round(duration / 60 / 60, 2),
            "summary": event['summary'] if 'summary' in event else ''
        })

    return massaged_events
