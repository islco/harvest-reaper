from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse
from datetime import datetime, timedelta
import json

from harvestreaper.googlecal.utils import get_calendar_events
from harvestreaper.harvest.models import HarvestToken, HarvestSubmission
from harvestreaper.harvest.utils import get_harvest_account, get_harvest_assignments, get_user_id


class LandingPageView(TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            return redirect('home')

        return super(LandingPageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['noscroll'] = True
        return context


class PrivacyPageView(TemplateView):
    template_name = 'privacy.html'


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

            # Make sure the token isn't expired for harvest
            if harvest_token.is_expired:
                harvest_token.refresh()

            kwargs['google'] = google_social_account
            kwargs['harvest'] = harvest_token
        else:
            return redirect('landing')

        return super(HomePageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        weeks = int(self.request.GET.get('weeks', 0))
        context['prev_week_url'] = reverse('home') + f'?weeks={weeks-1}'
        context['next_week_url'] = reverse('home') + f'?weeks={weeks+1}'

        google_social_account = kwargs.pop('google', None)
        harvest_token = kwargs.pop('harvest', None)

        # Only show import data if there are both valid tokens
        if google_social_account and harvest_token:
            token = google_social_account.socialtoken_set.first()

            # Google
            now = datetime.utcnow()
            # We add and subtract here to account for zero indexing and bring things
            # back to previous Sat.
            # Adding 4 to account for UTC
            start_day = now - timedelta(days=now.weekday() + 2) - \
                timedelta(weeks=-weeks, hours=now.hour - 4, minutes=now.minute)
            end_day = now + timedelta(days=5 - now.weekday()) - \
                timedelta(weeks=-weeks, hours=now.hour - 4, minutes=now.minute)
            massaged_events = get_calendar_events(token, start_day, end_day)
            if massaged_events is None:
                # There has been an error here so let's tell the user
                context['google_error'] = True
                return context
            context['sat_events'] = massaged_events['Sat']
            context['sun_events'] = massaged_events['Sun']
            context['mon_events'] = massaged_events['Mon']
            context['tue_events'] = massaged_events['Tue']
            context['wed_events'] = massaged_events['Wed']
            context['thu_events'] = massaged_events['Thu']
            context['fri_events'] = massaged_events['Fri']
            context['time_window'] = {
                'start': start_day.strftime('%b %d'),
                # Massage the end day to display the effective end date (i.e. the previous day)
                'end': (end_day - timedelta(days=1)).strftime('%b %d')
            }

            # Harvest
            account = get_harvest_account(harvest_token)
            user_id = get_user_id(harvest_token, account)
            projects = get_harvest_assignments(harvest_token, account, user_id)
            context['harvest_id'] = account
            context['harvest_projects'] = projects
            context['harvest_projects_json'] = json.dumps(projects)

            # Previous submissions
            previous_submission_qs = HarvestSubmission.objects \
                .filter(user=self.request.user).values_list(
                    'event_name', 'project_id', 'assignment_id')
            previous_submission_dict = json.dumps({
                sub[0].lower(): (sub[1], sub[2]) for sub in previous_submission_qs
            })
            context['previous_submission_values'] = previous_submission_dict

        return context
