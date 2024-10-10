from rest_framework import serializers

from apps.marketplace.models import MarketPlace, Produit

class ProduitSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = ['id_produit', 'description', 'price', 'currency', 'nombre', 'titre', 'marketplace']
        
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