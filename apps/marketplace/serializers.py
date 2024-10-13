from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from apps.marketplace.models import MarketPlace, Produit, AchatProduit, ImageProduit
from apps.client.serializers import ClientSerializer
from apps.client.models import Client
from apps.users.serializers import UserSerializer
from apps.users.models import User
from django.conf import settings

class ImageProduitSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageProduit
        fields = ['id_image_produit', 'image_url', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')
    
    def get_image_url(self,obj):
        return f'{settings.BASE_URL}api{obj.image.url}' if obj.image else None

class AchatProduitSerializer(serializers.ModelSerializer):
    acheteur = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = AchatProduit
        fields = ['id_achat', 'acheteur', 'created_at']

    def get_acheteur(self, obj):
        content_type = obj.acheteur_type

        if content_type == ContentType.objects.get_for_model(Client):
            acheteur_obj = Client.objects.get(id=obj.acheteur_id)
            return ClientSerializer(acheteur_obj).data

        if content_type == ContentType.objects.get_for_model(User):
            acheteur_obj = User.objects.get(id=obj.acheteur_id)
            return UserSerializer(acheteur_obj).data

        return None

    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y %H:%M:%S')

class ProduitSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    images = ImageProduitSerializer(many=True, read_only=True)
    
    class Meta:
        model = Produit
        fields = ['id_produit', 'description', 'price', 'currency', 'nombre', 'titre', 'marketplace', 'images', 'created_at']
        
    def get_created_at(self,obj):
        return obj.created_at.strftime('%d-%m-%Y')

   
class MarketPlaceSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    produits = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketPlace
        fields = ['id_marketplace', 'produits', 'created_at']
        
    def get_created_at(self,obj):
        return obj.created_at.strftime('%d-%m-%Y')
    
    def get_produits(self,obj):
        return ProduitSerializer(obj.produits, many=True).data