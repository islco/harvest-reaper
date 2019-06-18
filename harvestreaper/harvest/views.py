from django.views.generic import RedirectView
from django.http import (
    HttpResponseNotAllowed, HttpResponseRedirect,
)
from requests import post
from datetime import datetime, timedelta

from harvestreaper.settings import HARVEST_CLIENT_ID, HARVEST_CLIENT_SECRET
from harvestreaper.harvest.models import HarvestToken

HARVEST_AUTH_URL = 'https://id.getharvest.com'
HARVEST_API_URL = 'https://api.harvestapp.com/api/v2/'


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

        # Go out and get the actual token
        request_data = {
            'code': auth_code,
            'client_id': HARVEST_CLIENT_ID,
            'client_secret': HARVEST_CLIENT_SECRET,
            'grant_type': 'authorization_code'
        }
        response = post(
            f'{HARVEST_AUTH_URL}/api/v2/oauth2/token', json=request_data)
        json = response.json()

        # Save the token for use later!
        HarvestToken.objects.update_or_create(user=user,
                                              token=json.get('access_token'),
                                              token_secret=json.get('refresh_token'),
                                              scope=scope.split(':')[1],
                                              expires_at=datetime.utcnow() + timedelta(seconds=json.get('expires_in')))  # noqa

        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))
