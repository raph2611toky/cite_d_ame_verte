from rest_framework.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.client.views import ProfileClientView, LogoutClientView, LoginClientView, RegisterClientView

app_name = 'client'

urlpatterns = [
    path('client/profile/', ProfileClientView.as_view(), name='client_profile'), #GET
    path('client/login/', LoginClientView.as_view(), name='login'), # POST
    path('client/register/', RegisterClientView.as_view(), name='register'), # POST
    path('client/logout/', LogoutClientView.as_view(), name='logout'), # PUT
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)