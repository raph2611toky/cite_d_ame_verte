from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.client.serializers import ClientSerializer
from .models import ImageEvenement, FileEvenement, Emplacement, Evenement

from django.conf import settings

class ImageEvenementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageEvenement
        fields = ['id_image_evenement', 'image_url', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')
    
    def get_image_url(self,obj):
        return f'{settings.BASE_URL}api{obj.image.url}' if obj.image else None


class FileEvenementSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = FileEvenement
        fields = ['id_file_evenement', 'file_url', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')
        
    def get_file_url(self,obj):
        return f'{settings.BASE_URL}api{obj.file.url}' if obj.file else None


class EmplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emplacement
        fields = ['id_emplacement', 'name_emplacement', 'longitude', 'latitude']


class EvenementSerializer(serializers.ModelSerializer):
    organisateurs = UserSerializer(many=True, read_only=True)
    participants = ClientSerializer(many=True, read_only=True)
    emplacement = EmplacementSerializer(read_only=True)
    images = ImageEvenementSerializer(many=True, read_only=True)
    files = FileEvenementSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()
    date_debut = serializers.SerializerMethodField()
    date_fin = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            'id_evenement', 'name_evenement','description','date_debut','date_fin','type','nombre_place', 'organisateurs','participants','created_at','emplacement','images','files'
        ]
        
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')
    
    def get_date_debut(self, obj):
        return obj.date_debut.strftime('%d-%m-%Y')
    
    def get_date_fin(self, obj):
        return obj.date_fin.strftime('%d-%m-%Y')
    
        
    def validate(self, attrs):
        attrs['emplacement'] = self.context.get('evenement_data')['emplacement'][0] if isinstance(self.context.get('evenement_data')['emplacement'], list) else self.context.get('evenement_data')['emplacement']
        return attrs
        
