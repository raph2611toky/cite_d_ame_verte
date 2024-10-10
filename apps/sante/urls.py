from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    MenstruationListView, MenstruationNew, MenstruationPredictView,
    OvulationPredictView, WomanSymptomsNewView, WomanSymptomListView,
    WomanInfoView, WomanConfigureView
)

urlpatterns = [
    path('woman/info/', WomanInfoView.as_view(), name='woman info'), # GET
    path('menstruation/list/', MenstruationListView.as_view(), name='menstruation-list'),
    path('menstruation/new/', MenstruationNew.as_view(), name='menstruation-new'),
    path('menstruation/predict/', MenstruationPredictView.as_view(), name='menstruation-predict'),
    path('ovulation/predict/', OvulationPredictView.as_view(), name='ovulation-predict'),
    path('symptom/new/', WomanSymptomsNewView.as_view(), name='symptom-new'), # POST
    path('symptom/list/', WomanSymptomListView.as_view(), name='symptom-list'), # GET
    path('woman/configure/', WomanConfigureView.as_view(), name='woman configure'), #POST
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
