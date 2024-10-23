from rest_framework.permissions import BasePermission
from apps.medical.models import Doctor
from config.helpers.helper import get_token_from_request, get_client
from django.contrib.auth.models import AnonymousUser

class IsAuthenticatedDoctor(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                request.doctor = Doctor.objects.get(user=request.user)
                return True
            except Doctor.DoesNotExist:
                return False
        return False

class IsAuthenticatedWomanOrDoctor(BasePermission):
    def has_permission(self, request, view):
        is_woman = is_doctor = False
        request.is_doctor = is_doctor
        request.is_woman = is_woman
        if request.user and request.user.is_authenticated:
            try:
                request.doctor = Doctor.objects.get(user=request.user)
                request.is_doctor = True
                return True
            except Doctor.DoesNotExist:
                return False
        token = get_token_from_request(request)
        if not token:
            return False

        client = get_client(token)
        if client is None or isinstance(client, AnonymousUser):
            return False
        if not client.is_active or client.sexe != 'F':
            return False
        request.woman = client.woman
        request.is_woman = True
        return True