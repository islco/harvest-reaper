from django.views.generic import RedirectView, TemplateView
from django.http import (
    HttpResponseNotAllowed, HttpResponseRedirect,
)
from datetime import datetime

from harvestreaper.settings import HARVEST_CLIENT_ID
from harvestreaper.harvest.utils import (
    HARVEST_AUTH_URL, get_harvest_token, post_harvest_time_entry)
from harvestreaper.harvest.models import HarvestToken
from harvestreaper.googlecal.utils import STRPTIME_UTIL


class HarvestOAuthView(RedirectView):
    url = f'{HARVEST_AUTH_URL}/oauth2/authorize?client_id={HARVEST_CLIENT_ID}&response_type=code'


class HarvestOAuthSuccessView(RedirectView):
    pattern_name = 'home'

    def get(self, request, *args, **kwargs):
        auth_code = request.GET.get('code', '')
        scope = request.GET.get('scope', '')
        user = request.user
        if not auth_code or not scope or not user.is_authenticated:
            return HttpResponseNotAllowed(['GET'])

        token, token_secret, expires_at = get_harvest_token(
            code=auth_code, code_key='code', grant_type='authorization_code')
        HarvestToken.objects.update_or_create(user=user,
                                              token=token,
                                              token_secret=token_secret,
                                              scope=scope.split(':')[1],
                                              expires_at=expires_at)  # noqa

        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))


class HarvestTimeSubmitView(TemplateView):
    http_method_names = ['post']
    template_name = 'time_submit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form_data = request.POST

        entries = [
            ('sat', form_data.get('satentries', 0)),
            ('sun', form_data.get('sunentries', 0)),
            ('mon', form_data.get('monentries', 0)),
            ('tue', form_data.get('tueentries', 0)),
            ('wed', form_data.get('wedentries', 0)),
            ('thu', form_data.get('thuentries', 0)),
            ('fri', form_data.get('frientries', 0)),
        ]
        account_id = form_data.get('harvestid', 0)
        successfully_submitted_entries = []

        # Iterate over every possible calendar entry and submit to Harvest
        for entry in entries:
            for i in range(int(entry[1]) + 1):
                index_val = f'{entry[0]}-{i}'
                assignment = form_data.get(f'assignment-{index_val}', None)
                # No assignment means that the data shouldn't be sent
                if not assignment or assignment == 'ignore':
                    continue

                project = form_data.get(f'project-{index_val}', None)
                duration = form_data.get(f'duration-{index_val}', None)
                notes = form_data.get(f'notes-{index_val}', None)
                raw_time = form_data.get(f'time-{index_val}', None)

                if project and duration and raw_time:
                    harvest_token = HarvestToken.objects.filter(user=self.request.user).first()
                    time = datetime.strptime(raw_time, STRPTIME_UTIL)
                    submitted_entry = post_harvest_time_entry(
                        harvest_token, account_id, project, assignment, time, duration, notes)
                    if submitted_entry is not None:
                        successfully_submitted_entries.append(submitted_entry)

        if len(successfully_submitted_entries) > 0:
            massaged_entries = {
                'Saturday': [],
                'Sunday': [],
                'Monday': [],
                'Tuesday': [],
                'Wednesday': [],
                'Thursday': [],
                'Friday': []
            }
            totals = {
                'Saturday': 0,
                'Sunday': 0,
                'Monday': 0,
                'Tuesday': 0,
                'Wednesday': 0,
                'Thursday': 0,
                'Friday': 0,
                'All': 0
            }

            for submission in successfully_submitted_entries:
                sub_date = submission.get('date')
                hrs = submission['hours']
                massaged_entries[sub_date].append(submission)
                totals[sub_date] += hrs
                totals['All'] += hrs

            context['entries'] = massaged_entries
            context['totals'] = totals

        return self.render_to_response(context)
