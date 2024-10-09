from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model, authenticate
from config.helpers.helper import get_token_from_request, get_client, get_user
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class UserOrClientAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        token = get_token_from_request(request)
        if token:
            client = get_client(token)
            if client is None or isinstance(client, AnonymousUser):
                request.client = AnonymousUser()
            elif not client.is_active:
                request.client = AnonymousUser()
            else:
                request.client = client
                return (None, token)
            user = get_user(token)
            if user is None or isinstance(user, AnonymousUser):
                request.user = AnonymousUser()
            elif not user.is_active:
                request.user = AnonymousUser()
            else:
                request.user = user
                return (user, token)
        return None