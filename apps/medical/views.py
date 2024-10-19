from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.medical.permissions import IsAuthenticatedDoctor
from apps.medical.models import Doctor, Appointment, Consultation, Speciality, VideoCallSession
from apps.medical.serializers import DoctorSerializer, AppointmentSerializer, ConsultationSerializer,VideoCallSessionSerializer
from apps.client.serializers import ClientSerializer
from apps.client.permissions import IsAuthenticatedClient
from django.contrib.auth.models import AnonymousUser

from config.helpers.authentications import UserOrClientAuthentication
from config.helpers.permissions import IsAuthenticatedUserOrClient
from config.helpers.helper import choose_doctor_and_get_date_time

from uuid import uuid4

def create_video_session(appointment, date_time):
    room_name = f"room_{uuid4()}"
    session = VideoCallSession.objects.create(
        appointment=appointment,
        room_name=room_name,
        started_at=date_time
    )
    return session

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

class ClientInfoMedicalView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []
    
    def get(self, request):
        try:
            client = request.client
            appointments = AppointmentSerializer(client.appointments.all(), many=True).data
            consultations = [ConsultationSerializer(appointment.consultation).data for appointment in client.appointments.all()]
            return Response({'appointments':appointments, 'consultations':consultations}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AskAppointementView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []
    
    def validate_data(self, data):
        try:
            keys = ['speciality', 'ask_level']
            if any(key not in data.keys()for key in keys):
                return False
            if data['ask_level'] not in ['CW', 'UR', 'CR']:
                return False
            return Speciality.objects.filter(id_speciality=data['speciality']).exists()
        except Exception:
            return False
        
    def ask_appointment(self, data, client):
        try:
            speciality = Speciality.objects.get(id_speciality=data['speciality'])
            if not self.validate_data(data):
                raise Exception({'erreur', 'Erreur de soummission des informations, veuillez verifier vos attributs et leurs valeurs'})
            doctor, _ = choose_doctor_and_get_date_time(speciality)
            Appointment.objects.create(doctor=doctor.id, patient=client.id, ask_level=data['ask_level'])
        except Exception as e:
            raise Exception({'erreur': str(e)})
    
    def post(self, request):
        try:
            self.ask_appointment(request.data, request.client.id)
            return Response({'message':'demande de rendez-vous reussi'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
class ConfirmAppointementView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []
    
    def validate_data(self, data):
        try:
            keys = ['appointment', 'status']
            if any(key not in data.keys()for key in keys):
                return False
            if data['status'] not in ['confirmed', 'cancelled']:
                return False
            return Appointment.objects.filter(id_appointment=data['appointment']).exists()
        except Exception:
            return False
    
    def post(self, request):
        try:
            # request.data = ['appointment', 'status']
            if not self.validate_data(request.data):
                return Response({'erreur', 'Erreur de soummission des informations, veuillez verifier vos attributs et leurs valeurs'}, status=status.HTTP_400_BAD_REQUEST)
            appointment = Appointment.objects.get(id_appointment=request.data['appointment'])
            _, date_time = choose_doctor_and_get_date_time(appointment.doctor.speciality)
            status_data = request.data['status']
            if status_data=='confirmed':
                appointment.date_time = date_time
                appointment.status = status_data
                appointment.save()
                session = create_video_session(appointment, date_time)
                return Response({'session':VideoCallSessionSerializer(session).data})
            appointment.status = status_data
            STATUS_MESSAGE = {'confirmed':'accépté', 'cancelled':'rejété'}
            appointment.save()
            return Response({'message':f'demande de rendez-vous {STATUS_MESSAGE[status_data]}'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
          