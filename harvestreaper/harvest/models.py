from django.db.models import ForeignKey, TextField, DateTimeField, IntegerField, CASCADE, Model
from datetime import datetime
import pytz

from harvestreaper.users.models import User
from harvestreaper.harvest.utils import get_harvest_token


class HarvestToken(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    token = TextField(
        verbose_name='token',
        help_text='"oauth_token" (OAuth1) or access token (OAuth2)')
    token_secret = TextField(
        verbose_name='token secret',
        help_text='"oauth_token_secret" (OAuth1) or refresh token (OAuth2)')
    scope = IntegerField(
        verbose_name='scope',
        help_text='Account id the token is associated with')
    expires_at = DateTimeField(verbose_name='expires at')

    class Meta:
        verbose_name = 'harvest application token'
        verbose_name_plural = 'harvest application tokens'

    def __str__(self):
        return self.token

    @property
    def is_expired(self):
        now = pytz.UTC.localize(datetime.now())
        if now > self.expires_at:
            return True

        return False

    def refresh(self):
        token, token_secret, expires_at = get_harvest_token(
            self.token_secret, 'refresh_token', 'refresh_token')

        self.token = token
        self.token_secret = token_secret
        self.expires_at = expires_at
        self.save()
