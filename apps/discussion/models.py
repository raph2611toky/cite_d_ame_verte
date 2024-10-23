from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone as django_timezone

from dotenv import load_dotenv
import os

load_dotenv()

from datetime import timedelta

def get_timezone():
    tz = os.getenv("TIMEZONE_HOURS")
    if '-' in tz:
        return django_timezone.now() - timedelta(hours=int(tz.strip()[1:]))
    return django_timezone.now()+timedelta(hours=int(tz))

class PlanningFamiliale(models.Model):
    id_pf = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100)
    
    sender_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    sender_id = models.PositiveIntegerField()
    sender = GenericForeignKey('sender_type', 'sender_id')
    
    is_online = models.BooleanField(default=False)
    titre = models.CharField(default='', max_length=100)
    created_at = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return self.description
    
    class Meta:
        db_table = 'planning_familiale'
    
class FilePlanningFamiliale(models.Model):
    id_file_pf = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='planningfamiliale/files/')
    planning_familiale = models.ForeignKey(PlanningFamiliale, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(default=get_timezone())

    def __str__(self):
        return self.file.name.split('/')[-1]
    
    class Meta:
        db_table = 'file_planning_familiale'
        
class Discussion(models.Model):
    CHOICES = [
        ('SS', 'Santé Séxuelle'),
        ('ME','Mere enceinte')
    ]
    id_discussion = models.AutoField(primary_key=True)
    
    members_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    members_id = models.PositiveIntegerField()
    members = GenericForeignKey('members_type', 'members_id')
    
    type = models.CharField(max_length=4, choices=CHOICES, default='SS')
    created_at = models.DateTimeField(default=get_timezone())
    
    class Meta:
        db_table = 'discussions'
        
class Message(models.Model):
    id_message = models.AutoField(primary_key=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='messages')
    
    sender_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    sender_id = models.PositiveIntegerField()     # Contient l'ID de l'objet (soit Client, soit User)
    sender = GenericForeignKey('sender_type', 'sender_id')
    
    contenu = models.CharField(max_length=240)
    created_at = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return self.contenu
    
    class Meta:
        db_table = 'message'
        
class FileMessage(models.Model):
    id_file_message = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='messages/files/')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return self.image.name.split('/')[-1]
    
    class Meta:
        db_table = 'file_message'