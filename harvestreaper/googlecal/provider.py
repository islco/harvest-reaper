from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider


class GoogleCalendarScopeProvider(GoogleProvider):
    id = 'googlecal'

    def get_default_scope(self):
        return ['profile', 'https://www.googleapis.com/auth/calendar']


provider_classes = [GoogleCalendarScopeProvider]
