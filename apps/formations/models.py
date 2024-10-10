from django.db import models
from apps.client.models import Client
from apps.users.models import User
from datetime import timedelta
from config.helpers.helper import get_timezone


class Formation(models.Model):
    id_formation = models.AutoField(primary_key=True)
    name_formation = models.CharField(max_length=100)
    description_formation = models.CharField(max_length=250)
    domaine = models.CharField(max_length=100)
    organisateurs = models.ManyToManyField(User, related_name='formations')
    participants = models.ManyToManyField(Client, related_name='formations')
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return self.name_formation
    
    class Meta:
        db_table = 'formations'
        
class FormationSession(models.Model):
    id_formationsession = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='sessions')
    is_online = models.BooleanField(default=False)
    titre = models.CharField(default='', max_length=100)
    created_at = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return self.description
    
    class Meta:
        db_table = 'formation_session'
    
class FileFormationSession(models.Model):
    id_file_session = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='formations/sessions/files/')
    formation_session = models.ForeignKey(FormationSession, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(default=get_timezone())

    def __str__(self):
        return self.file.name.split('/')[-1]
    
    class Meta:
        db_table = 'file_formation_session'

class FormationPayment(models.Model):
    id_formation_payment = models.AutoField(primary_key=True)
    formation = models.OneToOneField(Formation, on_delete=models.CASCADE, related_name='payments')
    organiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formation_payments')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=15, default='MGA')
    validity_days = models.IntegerField()

    def __str__(self):
        return f"{self.formation.name_formation} - {self.price} {self.currency}"

    class Meta:
        db_table = 'formation_payments'

class ClientFormationSubscription(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='formation_subscriptions')
    formation_payment = models.ForeignKey(FormationPayment, on_delete=models.CASCADE, related_name='client_subscriptions')
    start_date = models.DateTimeField(default=get_timezone())
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.client.email} - {self.formation_payment.formation.name_formation}"

    class Meta:
        db_table = 'client_formation_subscriptions'