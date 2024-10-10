from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.utils import timezone as django_timezone
from datetime import timedelta
import os

def get_timezone():
    tz = os.getenv("TIMEZONE_HOURS")
    if '-' in tz:
        return django_timezone.now() - timedelta(hours=int(tz.strip()[1:]))
    return django_timezone.now()+timedelta(hours=int(tz))

class MarketPlace(models.Model):
    id_marketplace = models.AutoField(primary_key=True)
    
    vendeur_type = models.OneToOneField(ContentType, on_delete=models.CASCADE)
    vendeur_id = models.PositiveIntegerField()     # Contient l'ID de l'objet (soit Client, soit User)
    vendeur = GenericForeignKey('vendeur_type', 'vendeur_id')
    
    created_at = models.DateTimeField(default=get_timezone())
    
    class Meta:
        db_table = 'marketplace'
        
class Produit(models.Model):
    id_produit = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(default='MGA', max_length=10)
    nombre = models.BigIntegerField(default=1)
    titre = models.CharField(max_length=100)
    marketplace = models.ForeignKey(MarketPlace, on_delete=models.CASCADE, related_name='produits')
    
    def __str__(self):
        return self.titre
    
    class Meta:
        db_table = 'produits'