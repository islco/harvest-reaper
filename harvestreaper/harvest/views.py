from django.views.generic import RedirectView, TemplateView
from django.http import (
    HttpResponseNotAllowed, HttpResponseRedirect,
)

from harvestreaper.settings import HARVEST_CLIENT_ID
from harvestreaper.harvest.utils import HARVEST_AUTH_URL, get_harvest_token
from harvestreaper.harvest.models import HarvestToken


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
        return self.render_to_response(context)
