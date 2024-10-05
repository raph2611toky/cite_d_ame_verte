from rest_framework.urls import path
from apps.users.views import ProfileView, LogoutView, LoginView, RegisterView

app_name = 'users'

urlpatterns = [
    path('user/profile/', ProfileView.as_view(), name='user_profile'), #GET
    path('user/login/', LoginView.as_view(), name='login'), # POST
    path('user/register/', RegisterView.as_view(), name='register'), # POST
    path('user/logout/', LogoutView.as_view(), name='logout'), # PUT
]