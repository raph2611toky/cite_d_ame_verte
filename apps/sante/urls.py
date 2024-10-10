from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    MenstruationListView, MenstruationNew, MenstruationPredictView,
    OvulationPredictView, WomanSymptomsNewView, WomanSymptomListView
)

urlpatterns = [
    path('menstruation/list/', MenstruationListView.as_view(), name='menstruation-list'),
    path('menstruation/new/', MenstruationNew.as_view(), name='menstruation-new'),
    path('menstruation/predict/', MenstruationPredictView.as_view(), name='menstruation-predict'),
    path('ovulation/predict/', OvulationPredictView.as_view(), name='ovulation-predict'),
    path('symptom/new/', WomanSymptomsNewView.as_view(), name='symptom-new'),
    path('symptom/list/', WomanSymptomListView.as_view(), name='symptom-list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
