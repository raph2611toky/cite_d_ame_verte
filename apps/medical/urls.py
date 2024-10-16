from django.urls import path
from apps.medical.views import DoctorListView, DoctorInfoView

urlpatterns = [
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctor/info/', DoctorInfoView.as_view(), name='doctor-info'),
]
