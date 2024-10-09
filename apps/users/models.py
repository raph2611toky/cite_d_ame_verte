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

class AccountMode(models.Model):
    id_account_mode = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=15, default='MGA')
    free_trial_days = models.IntegerField(default=0)
    validity_days = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'account_modes'

class User(AbstractUser):
    SEXE = [
        ('F', 'Féminin'),
        ('M', 'Masculin'),
        ('I', 'Inconnu')
    ]
    
    first_name = models.CharField(max_length=64, null=False)
    last_name = models.CharField(max_length=64, null=True)
    email = models.EmailField('email', unique=True)
    adress = models.CharField(max_length=100, default='Inconu')
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
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.email

    class Meta:
        db_table = 'users'
        
class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    account_mode = models.ForeignKey(AccountMode, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.account_mode.validity_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.account_mode.name}"

    class Meta:
        db_table = 'user_subscriptions'