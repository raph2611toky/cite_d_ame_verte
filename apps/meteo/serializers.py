from rest_framework import serializers
from .models import Location, Meteo, Cyclone, Inondation, Secheresse, AutreCatastrophe

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id_location', 'ville', 'pays', 'latitude', 'longitude']

class MeteoSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    
    class Meta:
        model = Meteo
        fields = ['id_meteo', 'date_observation', 'temperature', 'humidite', 'vent', 'location']


class CycloneSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    
    class Meta:
        model = Cyclone
        fields = ['id_cyclone', 'titre', 'description', 'date_debut', 'date_fin', 'niveau_alerte', 
                  'vitesse_vent_max', 'pression_min', 'rayon_max', 'location']


class InondationSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    
    class Meta:
        model = Inondation
        fields = ['id_inondation', 'titre', 'description', 'date_debut', 'date_fin', 'niveau_alerte', 
                  'surface_inondee', 'population_affectee', 'location']


class SecheresseSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    
    class Meta:
        model = Secheresse
        fields = ['id_secheresse', 'titre', 'description', 'date_debut', 'date_fin', 'niveau_alerte', 
                  'duree', 'surface_impactee', 'location']


class AutreCatastropheSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = AutreCatastrophe
        fields = ['id_catastrophe', 'titre', 'description', 'date_debut', 'date_fin', 'niveau_alerte', 
                  'type_catastrophe', 'location']
