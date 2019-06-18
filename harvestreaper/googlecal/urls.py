from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import GoogleCalendarScopeProvider


urlpatterns = default_urlpatterns(GoogleCalendarScopeProvider)
