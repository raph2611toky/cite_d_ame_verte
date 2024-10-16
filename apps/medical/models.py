from django.db import models

from apps.users.models import User
from apps.client.models import Client
from apps.evenements.models import Emplacement

from config.helpers.helper import get_timezone

class Speciality(models.Model):
    id_speciality = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'speciality'

class Doctor(models.Model):
    id_doctor = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)
    experience = models.IntegerField()
    location = models.ForeignKey(Emplacement, on_delete=models.CASCADE, related_name='doctors')
    
    def __str__(self):
        return self.user.first_name
    
    class Meta:
        db_table = 'doctor'

class Appointment(models.Model):
    id_appointment = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    patient = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments')
    date_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])
    
    def __str__(self):
        return f'< Appointment: {self.doctor} - {self.patient} >'
    
    class Meta:
        db_table = 'appointment'

class Consultation(models.Model):
    id_consultation = models.AutoField(primary_key=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    symptoms = models.TextField()
    diagnosis = models.TextField()
    prescription = models.TextField()
    consultation_date = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return f'{self.symptoms} : {self.diagnosis}'
    
    class Meta:
        db_table = 'consultation'