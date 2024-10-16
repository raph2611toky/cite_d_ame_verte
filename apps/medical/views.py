from rest_framework.views import APIView
from rest_framework.response import Response
from apps.medical.permissions import IsAuthenticatedDoctor
from apps.medical.models import Doctor, Appointment, Consultation, Doctor
from apps.medical.serializers import DoctorSerializer, AppointmentSerializer, ConsultationSerializer
from config.helpers.authentications import UserOrClientAuthentication
from config.helpers.permissions import IsAuthenticatedUserOrClient  

class DoctorListView(APIView):
    permission_classes = [IsAuthenticatedDoctor]

    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

class DoctorInfoView(APIView):
    permission_classes = [IsAuthenticatedDoctor]

    def get(self, request):
        doctor = request.doctor
        
        appointments = Appointment.objects.filter(doctor=doctor)
        patients = [appointment.patient for appointment in appointments]

        consultations = Consultation.objects.filter(appointment__doctor=doctor)

        data = {
            "doctor": DoctorSerializer(doctor).data,
            "patients": ClientSerializer(patients, many=True).data,
            "appointments": AppointmentSerializer(appointments, many=True).data,
            "consultations": ConsultationSerializer(consultations, many=True).data,
        }

        return Response(data)
