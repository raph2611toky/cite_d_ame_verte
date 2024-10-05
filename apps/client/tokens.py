from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
import uuid
from datetime import datetime, timezone, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone as django_timezone
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError
from apps.client.models import ClientOutstandingToken

class ClientRefreshToken(RefreshToken):
    @classmethod
    def for_client(cls, client):
        if client is None:
            raise TokenError("Client not provided")

        token = cls()
        token['client_id'] = client.id
        token['jti'] = str(uuid.uuid4())
        token.set_exp()
        
        if api_settings.BLACKLIST_AFTER_ROTATION:
            expires_at = datetime.fromtimestamp(token['exp'], tz=timezone.utc)
            ClientOutstandingToken.objects.create(
                client=client,
                jti=token['jti'],
                token=str(token),
                expires_at=expires_at
            )

        return token
    

    def set_exp(self, from_time=None, lifetime=None):
        if from_time is None:
            from_time = django_timezone.now()

        if lifetime is None:
            lifetime = api_settings.REFRESH_TOKEN_LIFETIME

        super().set_exp(from_time=from_time, lifetime=lifetime)

        self.access_token.set_exp(
            from_time=from_time,
            lifetime=api_settings.ACCESS_TOKEN_LIFETIME
        )
        
    def blacklist(self):
        try:
            outstanding_token = ClientOutstandingToken.objects.get(jti=self['jti'])
            outstanding_token.blacklisted = True
            outstanding_token.save()
        except ClientOutstandingToken.DoesNotExist:
            raise TokenError('Token not found for blacklisting.')


class ClientAccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.id) + six.text_type(timestamp) + six.text_type(user.is_email_verified)

account_activation_token = ClientAccountActivationTokenGenerator()
