from django.views.generic import TemplateView
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        google_social_account = None
        if hasattr(self.request.user, 'socialaccount_set'):
            google_social_account = self.request.user.socialaccount_set.filter(
                provider="googlecal").first()

        if google_social_account:
            token = google_social_account.socialtoken_set.first()
            creds = Credentials(token=token.token, refresh_token=token.token_secret)
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.utcnow().isoformat() + 'Z'
            try:
                events_result = service.events().list(calendarId='primary', timeMin=now,
                                                      maxResults=10, singleEvents=True,
                                                      orderBy='startTime').execute()
            except Exception as e:
                print(e)
                return context

            events = events_result.get('items', [])
            massaged_events = []
            for event in events:
                massaged_events.append({
                    "start": event['start'].get('dateTime', event['start'].get('date')),  # noqa
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "summary": event['summary']
                })

            context['upcoming_events'] = massaged_events

        return context
