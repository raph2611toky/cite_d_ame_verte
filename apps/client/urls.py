from rest_framework.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.client.views import (
        ProfileClientView, LogoutClientView, LoginClientView, RegisterClientView,
        ClientDepotView,ClientDepotVerification, PaymentVerificationStatusClientView, 
        ClientDepositVoucherClientView,
    )

app_name = 'client'

urlpatterns = [
    path('client/profile/', ProfileClientView.as_view(), name='client_profile'), #GET
    path('client/login/', LoginClientView.as_view(), name='login'), # POST
    path('client/register/', RegisterClientView.as_view(), name='register'), # POST
    path('client/logout/', LogoutClientView.as_view(), name='logout'), # PUT
    path('client/depots/', ClientDepotView.as_view(), name='client_depot'),#GET
    path('client/depositvoucher/', ClientDepositVoucherClientView.as_view(), name='client_depositvoucher'),#GET
    path('client/payement/verification/mobile/', ClientDepotVerification.as_view(), name='payment_verification'),# POST,
    path("client/payement/status/", PaymentVerificationStatusClientView.as_view(), name="payement_status"), #GET
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)