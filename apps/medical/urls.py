from django.urls import path
from apps.medical.views import DoctorListView, DoctorInfoView, AskAppointementView, ConfirmAppointementView,ClientInfoMedicalView

urlpatterns = [
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),#GET
    path('doctor/info/', DoctorInfoView.as_view(), name='doctor-info'),#GET
    path('medical/client/info/', ClientInfoMedicalView.as_view(), name='client medical info'), # GET
    path('doctor/appointment/ask/', AskAppointementView.as_view(), name='ask appointment'),#POST
    path('doctor/appointment/confirm/', ConfirmAppointementView.as_view(), name='confirm appointment'), #POST
]
