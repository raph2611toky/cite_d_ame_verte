from rest_framework.permissions import BasePermission
from config.helpers.helper import get_token_from_request, get_client
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import PermissionDenied

class IsAuthenticatedWoman(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.sexe == 'F':
                request.woman = request.user.woman
                return True
            else:
                raise PermissionDenied("Authorization failed: User is not female")

        token = get_token_from_request(request)
        if not token:
            return False

        client = get_client(token)
        if client is None or isinstance(client, AnonymousUser):
            return False

        if not client.is_active:
            return False

        if client.sexe == 'F':
            request.woman = client.woman
            request.client = client
            return True
        else:
            raise PermissionDenied("Authorization failed: Client is not female")

        return False
