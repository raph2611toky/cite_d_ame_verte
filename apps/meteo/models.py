from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
        
# Modèle pour les tremblements de terre
class TremblementDeTerre(Catastrophe):
    id_seisme = models.AutoField(primary_key=True)
    magnitude = models.FloatField()
    profondeur = models.FloatField()  # en km
    epicentre_latitude = models.FloatField()
    epicentre_longitude = models.FloatField()

    def __str__(self):
        return f"Tremblement de terre: {self.titre} ({self.magnitude}M)"

    class Meta:
        db_table = 'tremblement_de_terre'


# Modèle pour les tsunamis
class Tsunami(Catastrophe):
    id_tsunami = models.AutoField(primary_key=True)
    hauteur_max_vagues = models.FloatField()  # Hauteur maximale des vagues en mètres
    distance_parcourue = models.FloatField()  # Distance parcourue en km

    def __str__(self):
        return f"Tsunami: {self.titre} (Hauteur: {self.hauteur_max_vagues}m)"
    
    class Meta:
        db_table = 'tsunami'


class Degats(models.Model):
    id_degats = models.AutoField(primary_key=True)

    # Champs pour relier de manière polymorphique à n'importe quelle catastrophe
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    catastrophe_object = GenericForeignKey('content_type', 'object_id')

    pertes_humaines = models.IntegerField(null=True, blank=True)  # Nombre de morts
    cout_estime = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Coût estimé en millions de $
    infrastructures_detruites = models.TextField(null=True, blank=True)  # Liste ou description des infrastructures touchées
    
    def __str__(self):
        return f"Dégâts pour {self.catastrophe_object}"

    class Meta:
        db_table = 'degats'


class SourceDonnees(models.Model):
    id_source = models.AutoField(primary_key=True)
    nom_source = models.CharField(max_length=255)
    url_source = models.URLField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Source: {self.nom_source}"

    class Meta:
        db_table = 'source_donnees'



class AutreCatastrophe(Catastrophe):
    id_catastrophe = models.AutoField(primary_key=True)
    type_catastrophe = models.CharField(max_length=100)

    def __str__(self):
        return f"Catastrophe: {self.type_catastrophe} ({self.titre}, {self.niveau_alerte})"

    class Meta:
        db_table = 'catastrophe'