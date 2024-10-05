from rest_framework.permissions import BasePermission
from config.helpers.helper import get_token_from_request, get_client
from django.contrib.auth.models import AnonymousUser

class IsAuthenticatedClient(BasePermission):
    def has_permission(self, request, view):
        token = get_token_from_request(request)
        if not token: return False

        client = get_client(token)
        if client is None or isinstance(client, AnonymousUser):
            return False
        if not client.is_active:
            return False
        request.client = client
        return True
