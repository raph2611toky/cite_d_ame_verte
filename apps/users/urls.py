from rest_framework.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import ProfileView, LogoutView, LoginView, RegisterView

app_name = 'users'

urlpatterns = [
    path('users/profile/', ProfileView.as_view(), name='user_profile'), #GET
    path('users/login/', LoginView.as_view(), name='login'), # POST
    path('users/register/', RegisterView.as_view(), name='register'), # POST
    path('users/logout/', LogoutView.as_view(), name='logout'), # PUT
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)