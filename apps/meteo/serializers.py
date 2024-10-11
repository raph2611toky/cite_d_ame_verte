from rest_framework import serializers
from .models import Location, Meteo, Cyclone, Inondation, Secheresse, AutreCatastrophe, Degats, TremblementDeTerre, Tsunami

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

class TremblementDeTerreSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = TremblementDeTerre
        fields = ['id_seisme', 'titre', 'description', 'date_debut', 'date_fin', 'niveau_alerte', 
                  'magnitude', 'profondeur', 'epicentre_latitude', 'epicentre_longitude', 'location']


class TsunamiSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = Tsunami
        fields = ['id_tsunami', 'titre', 'description', 'date_debut', 'date_fin', 'niveau_alerte', 
                  'hauteur_max_vagues', 'distance_parcourue', 'location']


class DegatsSerializer(serializers.ModelSerializer):
    catastrophe_object = serializers.SerializerMethodField()

    class Meta:
        model = Degats
        fields = ['id_degats', 'catastrophe_object', 'pertes_humaines', 'cout_estime', 'infrastructures_detruites']

    def get_catastrophe_object(self, obj):
        """
        Dynamically handle the nested serialization of the catastrophe object (Cyclone, Inondation, etc.).
        """
        if isinstance(obj.catastrophe_object, Cyclone):
            return CycloneSerializer(obj.catastrophe_object).data
        elif isinstance(obj.catastrophe_object, Inondation):
            return InondationSerializer(obj.catastrophe_object).data
        elif isinstance(obj.catastrophe_object, Secheresse):
            return SecheresseSerializer(obj.catastrophe_object).data
        elif isinstance(obj.catastrophe_object, TremblementDeTerre):
            return TremblementDeTerreSerializer(obj.catastrophe_object).data
        elif isinstance(obj.catastrophe_object, Tsunami):
            return TsunamiSerializer(obj.catastrophe_object).data
        else:
            return None