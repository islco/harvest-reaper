from django.db.models import ForeignKey, TextField, DateTimeField, IntegerField, CASCADE, Model

from harvestreaper.users.models import User


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

    def expired(self):
        # TODO: Update this
        return False
