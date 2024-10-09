from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.formations.views import (
    FormationListView, 
    FormationProfileFindView, 
    FormationProfileView, 
    FormationNewView,
    #FormationPaymentView, 
    FormationSubscription,
    FormationSessionNewView
)

urlpatterns = [
    path('formations/list/', FormationListView.as_view(), name='formation-list'), # GET
    path('formations/<int:id_formation>/', FormationProfileFindView.as_view(), name='formation-detail'), # GET
    path('formations/<int:id_formation>/edit/', FormationProfileView.as_view(), name='formation-edit'), # PUT, DELETE
    path('formations/new/', FormationNewView.as_view(), name='formation-new'), # POST
    #path('formations/payments/', FormationPaymentView.as_view(), name='formation-payment'), # POST
    path('formations/subscribe/', FormationSubscription.as_view(), name='formation-subscribe'), # POST
    path('formation/sessions/new/', FormationSessionNewView.as_view(), name='new sessions'), # POST
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)