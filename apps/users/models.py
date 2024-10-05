from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from dotenv import load_dotenv
from datetime import timedelta

from apps.users.managers import UserManager
import os

load_dotenv()


def default_created_at():
    tz = os.getenv("TIMEZONE_HOURS")
    if tz.strip().startswith("-"):
        return timezone.now() - timedelta(hours=int(tz.replace("-","").strip()))
    return timezone.now() + timedelta(hours=int(tz))

class User(AbstractUser):
    SEXE = [
        ('F', 'Féminin'),
        ('M', 'Masculin'),
        ('I', 'Inconnu')
    ]
    
    first_name = models.CharField(max_length=64, null=False)
    last_name = models.CharField(max_length=64, null=True)
    email = models.EmailField('email', unique=True)
    contact = models.CharField(max_length=20, null=False)
    sexe = models.CharField(max_length=20, choices=SEXE, default='I')
    domaine = models.CharField(max_length=50)
    profession = models.CharField(max_length=50)
    organisation = models.CharField(max_length=100)
    credit_vert = models.IntegerField(default=0)
    profile = models.ImageField(upload_to='profiles/users/', default='profiles/users/default.png')

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.first_name.capitalize() + ' ' + self.last_name.capitalize()

    class Meta:
        db_table = 'users'