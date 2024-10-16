from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from dotenv import load_dotenv
from datetime import timedelta
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from apps.marketplace.models import MarketPlace, AchatProduit
from apps.sante.models import Woman

from apps.users.managers import UserManager
import os
from decimal import Decimal

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
    credit_vert = models.BigIntegerField(default=0)
    domaine = models.CharField(max_length=50)
    profession = models.CharField(max_length=50)
    organisation = models.CharField(max_length=100)
    credit_vert = models.IntegerField(default=0)
    profile = models.ImageField(upload_to='profiles/users/', default='profiles/users/default.png')

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    @property
    def marketplace(self):
        content_type = ContentType.objects.get_for_model(self)
        try:
            marketplace, created = MarketPlace.objects.get_or_create(
                vendeur_type=content_type,
                vendeur_id=self.id
            )
        except MarketPlace.DoesNotExist:
            marketplace = MarketPlace.objects.create(
                vendeur_type=content_type,
                vendeur_id=self.id
            )
        return marketplace
    
    @property
    def achats(self):
        content_type = ContentType.objects.get_for_model(self)
        return AchatProduit.objects.filter(acheteur_type=content_type, acheteur_id=self.id)

    def new_achat(self, produit):
        content_type = ContentType.objects.get_for_model(self)
        achat = AchatProduit.objects.create(acheteur_type=content_type, acheteur_id=self.id)
        WITH_PAYMENT_MONEY = bool(os.getenv("WITH_PAYMENT_MONEY"))
        if WITH_PAYMENT_MONEY:
            self.soustract_voucher(produit.price)
            vendeur = produit.marketplace.vendeur
            vendeur.add_voucher(produit.price)
        produit.achateurs.add(achat)
        return achat
    
    def add_voucher(self, solde):
        user_voucher = self.vouchers
        user_voucher += Decimal(solde)
        user_voucher.save()
        
    def soustract_voucher(self, solde):
        user_voucher = self.vouchers
        user_voucher -= Decimal(solde)
        user_voucher.save()

    @property
    def woman(self):
        if self.sexe == 'F':
            content_type = ContentType.objects.get_for_model(self)
            woman, created = Woman.objects.get_or_create(
                woman_type=content_type,
                woman_id=self.id
            )
            return woman
        return None

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
        
#####################################################
#                 PAYEMENT MOBILE                   #
#####################################################

class PayementTemplateUser(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Success'),
        ('F', 'Failed')
    ]
    
    PAYEMENT_MODES = (
        ('M','Mvola'),
        ('A', 'Airtel Money'),
        ('O', 'Orange Money')
    )
    
    numero_source = models.CharField(max_length=15)
    reference = models.CharField(max_length=100)
    date_payement = models.DateField()
    mode_payement = models.CharField(max_length=1, choices=PAYEMENT_MODES, default='P')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.reference
    
    class Meta:
        abstract = True

class DepotUser(PayementTemplateUser):
    CURRENCY = (
        ('MGA', 'Ariary'),
    )
    
    id_depot = models.AutoField(primary_key=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY, default='MGA')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='depots')
    
    class Meta: 
        db_table = 'depotuser'

class DepositVoucherUser(models.Model):
    id_depositvoucher = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vouchers')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(default=default_created_at())

    def __str__(self):
        return f"Voucher {self.id} - {self.user} - {self.amount}"

    class Meta:
        db_table = 'depositvoucheruser'

class QueuePaymentVerificationUser(PayementTemplateUser):
    id_queuepayement = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queues')
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'queuepayementverificationuser'