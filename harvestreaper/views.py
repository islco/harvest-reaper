from django.views.generic import TemplateView
from django.shortcuts import redirect
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from harvestreaper.harvest.models import HarvestToken


class HomePageView(TemplateView):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            google_social_account = None
            if hasattr(self.request.user, 'socialaccount_set'):
                google_social_account = self.request.user.socialaccount_set.filter(
                    provider="googlecal").first()
            harvest_token = HarvestToken.objects.filter(user=self.request.user).first()

            # Get a harvest token if necessary
            if not harvest_token:
                return redirect('harvest_auth')

            # Make sure the token isn't expired for harvest (google done automatically)
            if harvest_token.is_expired:
                harvest_token.refresh()

            kwargs['google'] = google_social_account
            kwargs['harvest'] = harvest_token

        return super(HomePageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        google_social_account = kwargs.pop('google', None)
        harvest_token = kwargs.pop('harvest', None)

        # Only show import data if there are both valid tokens
        if google_social_account and harvest_token:
            # TODO: Refactor this into a util or something. No real need to be here
            token = google_social_account.socialtoken_set.first()
            creds = Credentials(token=token.token, refresh_token=token.token_secret)
            service = build('calendar', 'v3', credentials=creds)

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
