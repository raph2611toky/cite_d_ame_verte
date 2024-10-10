from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.formations.views import (
    FormationListView,
    FormationFilterView, 
    FormationProfileFindView, 
    FormationProfileView, 
    FormationNewView,
    #FormationPaymentView, 
    FormationSubscription,
    FormationSessionNewView,
    FormationSessionFindView,
    FormationSessionProfileView
)

urlpatterns = [
    path('formations/list/', FormationListView.as_view(), name='formation-list'), # GET
    path('formations/filter/', FormationFilterView.as_view(), name='formation_filter'), # GET
    path('formations/<int:id_formation>/', FormationProfileFindView.as_view(), name='formation-detail'), # GET
    path('formations/<int:id_formation>/edit/', FormationProfileView.as_view(), name='formation-edit'), # PUT, DELETE
    path('formations/new/', FormationNewView.as_view(), name='formation-new'), # POST
    #path('formations/payments/', FormationPaymentView.as_view(), name='formation-payment'), # POST
    path('formations/subscribe/', FormationSubscription.as_view(), name='formation-subscribe'), # POST
    path('formation/sessions/new/', FormationSessionNewView.as_view(), name='new sessions'), # POST
    path('formation/session/profile/find/<int:id_formationsession>/', FormationSessionFindView.as_view(), name='formation find '), # GET
    path('formation/session/profile/<int:id_formationsession>/', FormationSessionProfileView.as_view(), name='session profile'), # DELETE
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)