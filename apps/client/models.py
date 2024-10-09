from django.db import models
from django.contrib.auth.hashers import make_password
from datetime import timedelta
from django.utils import timezone as django_timezone

import os

def get_timezone():
    tz = os.getenv("TIMEZONE_HOURS")
    if '-' in tz:
        return django_timezone.now() - timedelta(hours=int(tz.strip()[1:]))
    return django_timezone.now()+timedelta(hours=int(tz))

class Client(models.Model):
    SEXE = [
        ('F', 'Féminin'),
        ('M', 'Masculin'),
        ('I', 'Inconnu')
    ]
    
    first_name = models.CharField(max_length=125)
    last_name = models.CharField(max_length=125, default='')
    email = models.EmailField()
    password = models.TextField()
    contact = models.CharField(max_length=100)
    adress = models.CharField(max_length=100)
    sexe = models.CharField(max_length=20, choices=SEXE, default='I')
    is_active = models.BooleanField(default=False)
    credit_vert = models.IntegerField(default=0)
    profile = models.ImageField(upload_to='profiles/client/', default='profiles/client/default.png')
    last_login = models.DateTimeField(default=get_timezone())
    joined_at = models.DateTimeField(default=get_timezone())
    
    @property
    def is_authenticated(self):
        return True 

    def set_password(self, new_password):
        self.password = make_password(new_password)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta: 
        db_table = "client"
        

class ClientOutstandingToken(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='outstanding_tokens')
    jti = models.CharField(max_length=255, unique=True)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    blacklisted = models.BooleanField(default=False)

    def is_expired(self):
        return self.expires_at <= get_timezone()
    
    class Meta:
        db_table = 'clientoutstandingtoken'