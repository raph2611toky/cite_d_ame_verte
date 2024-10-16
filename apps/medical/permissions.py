from rest_framework.permissions import BasePermission
from apps.medical.models import Doctor

class IsAuthenticatedDoctor(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                request.doctor = Doctor.objects.get(user=request.user)
                return True
            except Doctor.DoesNotExist:
                return False
        return False
