from django.db import models
from apps.users.models import User
from apps.client.models import Client
from config.helpers.helper import get_timezone

        
class Emplacement(models.Model):
    id_emplacement = models.AutoField(primary_key=True)
    name_emplacement = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()
    
    def __str__(self):
        return f'({self.longitude}, {self.latitude})'
    
    class Meta:
        db_table = 'emplacement'

class Evenement(models.Model):
    TYPE = [
        ('V', 'Virtuel'),
        ('P', 'Physique')
    ]
    id_evenement = models.AutoField(primary_key=True)
    name_evenement = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    date_debut = models.DateTimeField(default=get_timezone())
    date_fin = models.DateTimeField(default=get_timezone())
    type = models.CharField(max_length=100, choices=TYPE, default='P')
    emplacement = models.ForeignKey(Emplacement, on_delete=models.CASCADE, related_name='evenements')
    organisateurs = models.ManyToManyField(User, related_name='evenements')
    participants = models.ManyToManyField(Client, related_name='evenements')
    created_at = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return self.name_evenement + ' : ' + self.description
    
    class Meta:
        db_table = 'evenements'

class ImageEvenement(models.Model):
    id_image_evenement = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='evenements/images/')
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(default=get_timezone())
    
    def __str__(self):
        return self.image.name.split('/')[-1]
    
    class Meta:
        db_table = 'image_evenement'
        
class FileEvenement(models.Model):
    id_file_evenement = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='evenements/files/')
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(default=get_timezone())

    def __str__(self):
        return self.file.name.split('/')[-1]
    
    class Meta:
        db_table = 'file_evenement'