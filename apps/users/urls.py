from rest_framework.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import (
        ProfileView, LogoutView, LoginView, RegisterView, AccountModeListView, ConfigureAccountMode,
        UserDepotView,UserDepotVerification, PaymentVerificationStatusUserView, 
        UserDepositVoucherUserView,
    )

app_name = 'users'

urlpatterns = [
    path('users/profile/', ProfileView.as_view(), name='user_profile'), #GET
    path('users/login/', LoginView.as_view(), name='login'), # POST
    path('users/register/', RegisterView.as_view(), name='register'), # POST
    path('users/logout/', LogoutView.as_view(), name='logout'), # PUT
    path('accountsmode/list/', AccountModeListView.as_view(), name='accounts_mode'), # GET
    path('users/configure/account_mode/', ConfigureAccountMode.as_view(), name='configure_account_mode'), # POST
    path('users/depots/', UserDepotView.as_view(), name='client_depot'),#GET
    path('users/depositvoucher/', UserDepositVoucherUserView.as_view(), name='client_depositvoucher'),#GET
    path('users/payement/verification/mobile/', UserDepotVerification.as_view(), name='payment_verification'),# POST,
    path("users/payement/status/", PaymentVerificationStatusUserView.as_view(), name="payement_status"), #GET
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)