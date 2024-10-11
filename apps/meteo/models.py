from django.db import models

# Modèle de localisation pour représenter les villes et coordonnées associées
class Location(models.Model):
    id_location = models.AutoField(primary_key=True)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100, default="Madagascar")
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.ville}, {self.pays}"
    
    class Meta:
        db_table = 'location'


class Meteo(models.Model):
    id_meteo = models.AutoField(primary_key=True)
    date_observation = models.DateTimeField()
    temperature = models.FloatField(null=True, blank=True)
    humidite = models.FloatField(null=True, blank=True)
    vent = models.FloatField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"Météo du {self.date_observation} à {self.location}"
    
    class Meta:
        db_table = 'meteo'


# Modèle générique pour les catastrophes
class Catastrophe(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField(null=True, blank=True)
    niveau_alerte = models.CharField(max_length=50)  # Ex: "vert", "orange", "rouge"
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Catastrophe: {self.titre} ({self.niveau_alerte})"
    


# Modèle pour les cyclones
class Cyclone(Catastrophe):
    id_cyclone = models.AutoField(primary_key=True)
    vitesse_vent_max = models.FloatField()
    pression_min = models.FloatField()
    rayon_max = models.FloatField()

    def __str__(self):
        return f"Cyclone: {self.titre} ({self.niveau_alerte})"
    
    class Meta:
        db_table = 'cyclone'


class Inondation(Catastrophe):
    id_inondation = models.AutoField(primary_key=True)
    surface_inondee = models.FloatField()  # Surface inondée en km²
    population_affectee = models.IntegerField()

    def __str__(self):
        return f"Inondation: {self.titre} ({self.niveau_alerte})"
    
    class Meta:
        db_table = 'inondation'


class Secheresse(Catastrophe):
    id_secheresse = models.AutoField(primary_key=True)
    duree = models.IntegerField()
    surface_impactee = models.FloatField()

    def __str__(self):
        return f"Sécheresse: {self.titre} ({self.niveau_alerte})"
    
    class Meta:
        db_table = 'secheresse'


class AutreCatastrophe(Catastrophe):
    id_catastrophe = models.AutoField(primary_key=True)
    type_catastrophe = models.CharField(max_length=100)

    def __str__(self):
        return f"Catastrophe: {self.type_catastrophe} ({self.titre}, {self.niveau_alerte})"

    class Meta:
        db_table = 'catastrophe'