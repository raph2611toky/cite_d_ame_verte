from rest_framework import serializers

from apps.medical.models import Speciality, Doctor, Appointment, Consultation, VideoCallSession
from apps.client.serializers import ClientSerializer
from apps.users.serializers import UserSerializer
from apps.evenements.serializers import EmplacementSerializer

class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ['id_speciality', 'name', 'description']

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    speciality = SpecialitySerializer()
    location = EmplacementSerializer()

    class Meta:
        model = Doctor
        fields = ['id_doctor', 'user', 'speciality', 'location']
        
class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer()
    patient = ClientSerializer()
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id_appointment', 'doctor', 'patient', 'date_time', 'status']

    def get_date_time(self, obj):
        return obj.date_time.strftime("%d-%m-%Y %H:%M:%S")
    
class ConsultationSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer()
    consultation_date = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = ['id_consultation', 'appointment', 'symptoms', 'diagnosis', 'prescription', 'consultation_date']
        
    def get_consultation_date(self, obj):
        return obj.consultation_date.strftime('%d-%m-%Y %H:%M:%S')
    
class VideoCallSessionSerializer(serializers.ModelSerializer):
    started_at = serializers.SerializerMethodField()
    ended_at = serializers.SerializerMethodField()

    class Meta:
        model = VideoCallSession
        fields = ['id_session', 'appointment', 'room_name', 'started_at', 'ended_at']
    
    def get_started_at(self, obj):
        return obj.started_at.strftime("%d-%m-%Y %H:%M:%S")
    
    def get_ended_at(self, obj):
        return obj.ended_at.strftime("%d-%m-%Y %H:%M:%S")