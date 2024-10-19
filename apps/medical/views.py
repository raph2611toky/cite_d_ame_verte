from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.medical.permissions import IsAuthenticatedDoctor
from apps.medical.models import Doctor, Appointment, Consultation, Doctor
from apps.medical.serializers import DoctorSerializer, AppointmentSerializer, ConsultationSerializer
from apps.client.serializers import ClientSerializer
from apps.client.permissions import IsAuthenticatedClient

from config.helpers.authentications import UserOrClientAuthentication
from config.helpers.permissions import IsAuthenticatedUserOrClient  

from datetime import datetime


class DoctorListView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]

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

class AskAppointementView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []
    
    def validate_data(self, data):
        try:
            keys = ['doctor', 'ask_level']
            if any(key not in data.keys()for key in keys):
                return False
            if data['ask_level'] not in ['CW', 'UR', 'CR']:
                return False
            return Doctor.objects.filter(id_doctor=data['doctor']).exists()
        except Exception:
            return False
    
    def post(self, request):
        try:
            # request.data = ['doctor', 'ask_level':CW, 'ask_level':CW,UR,CR]
            if not self.validate_data(request.data):
                return Response({'erreur', 'Erreur de soummission des informations, veuillez verifier vos attributs et leurs valeurs'}, status=status.HTTP_400_BAD_REQUEST)
            Appointment.objects.create(doctor=request.data['doctor'], patient=request.client.id, ask_level=request.data['ask_level'])
            return Response({'message':'demande de rendez-vous reussi'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
class ConfirmAppointementView(APIView):
    permission_classes = [IsAuthenticatedDoctor]
    
    def validate_data(self, data):
        try:
            keys = ['appointment', 'date_time', 'status']
            if any(key not in data.keys()for key in keys):
                return False
            if data['status'] not in ['confirmed', 'cancelled']:
                return False
            return Appointment.objects.filter(id_appointment=data['appointment']).exists()
        except Exception:
            return False
    
    def post(self, request):
        try:
            # request.data = ['appointment', 'date_time', 'status']
            if not self.validate_data(request.data):
                return Response({'erreur', 'Erreur de soummission des informations, veuillez verifier vos attributs et leurs valeurs'}, status=status.HTTP_400_BAD_REQUEST)
            appointment = Appointment.objects.get(id_appointment=request.data['appointment'])
            status_data = request.data['status']
            if status_data=='confirmed':
                appointment.date_time = datetime.strptime(request.data['date_time'].strip(), '%Y-%m-%d %H:%M:%S')
            appointment.status = status_data
            STATUS_MESSAGE = {'confirmed':'accépté', 'cancelled':'rejété'}
            appointment.save()
            return Response({'message':f'demande de rendez-vous {STATUS_MESSAGE[status_data]}'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
            