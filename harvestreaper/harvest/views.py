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
            return HttpResponseNotAllowed()

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
        calendar_entries = form_data.get('calendarentries', 0)
        account_id = form_data.get('harvestid', 0)

        # Iterate over every possible calendar entry and submit to Harvest
        for i in range(int(calendar_entries) + 1):
            assignment = form_data.get(f'assignment-{i}', None)
            # No assignment means that the data shouldn't be sent
            if not assignment:
                continue

            project = form_data.get(f'project-{i}', None)
            duration = form_data.get(f'duration-{i}', None)
            raw_time = form_data.get(f'time-{i}', None)

            if project and duration and raw_time:
                harvest_token = HarvestToken.objects.filter(user=self.request.user).first()
                time = datetime.strptime(raw_time, STRPTIME_UTIL)

                created_entry = post_harvest_time_entry(
                    harvest_token, account_id, project, assignment, time, duration)

        # TODO: Add to context

        return self.render_to_response(context)
