from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

from apps.marketplace.models import Produit, MarketPlace, ImageProduit
from apps.marketplace.serializers import ProduitSerializer, AchatProduitSerializer

from config.helpers.permissions import IsAuthenticatedUserOrClient
from config.helpers.authentications import UserOrClientAuthentication

from dotenv import load_dotenv
import traceback
import os

load_dotenv()

class ProduitsListView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]
    
    def get(self, request):
        try:
            produits = Produit.objects.all()
            serializer = ProduitSerializer(produits, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProduitFilterView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request):
        try:
            if hasattr(request, 'client'):
                produits = Produit.objects.filter(marketplace__vendeur_id=request.client.id)
            else:
                produits = Produit.objects.filter(marketplace__vendeur_id=request.user.id)
            serializer = ProduitSerializer(produits, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProduitProfileFindView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request, id_produit):
        try:
            produit = Produit.objects.get(id_produit=id_produit)
            return Response(ProduitSerializer(produit).data, status=status.HTTP_200_OK)
        except Produit.DoesNotExist:
            return Response({'erreur':'Produit inexistant'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProduitProfileView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]
    
    def validate_data(self, data):
        try:
            keys = ['description', 'price', 'nombre', 'titre']#, 'currency']
            if any(key not in data.keys()for key in keys):
                return False
            return True
        except Exception:
            return False
    
    def put(self, request, id_produit):
        try:
            # request.data = ['description', 'price', 'currency', 'nombre', 'titre']
            if not self.validate_data(request.data):
                return Response({'erreur':'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            produit = Produit.objects.get(id_produit=id_produit)
            if hasattr(request, 'client'):
                if produit not in request.client.marketplace.produits.all():
                    return Response({'erreur':'Vous n\'avez pas l\'autorisation de faire cette action'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                produits = Produit.objects.filter(marketplace__vendeur_id=request.user.id)
                if produit not in produits:
                    return Response({'erreur':'Vous n\'avez pas l\'autorisation de faire cette action'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = ProduitSerializer(produit, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id_produit):
        try:
            produit = Produit.objects.get(id_produit=id_produit)
            if hasattr(request, 'client'):
                if produit not in request.client.marketplace.produits.all():
                    return Response({'erreur':'Vous n\'avez pas l\'autorisation de faire cette action'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                produits = Produit.objects.filter(marketplace__vendeur_id=request.user.id)
                if produit not in produits:
                    return Response({'erreur':'Vous n\'avez pas l\'autorisation de faire cette action'}, status=status.HTTP_401_UNAUTHORIZED)
            produit.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProduitNewView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]
    
    def validate_data(self, data):
        try:
            keys = ['description', 'price', 'nombre', 'titre']#, 'currency']
            if any(key not in data.keys()for key in keys):
                return False
            return True
        except Exception:
            return False
    
    def post(self, request):
        # request.data = ['description', 'price', 'currency', 'nombre', 'titre']
        # request.FILES = ['images']
        try:
            if not self.validate_data(request.data):
                return Response({'erreur':'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            produit_data = request.data
            images = request.FILES.gelist('images')
            IS_CLIENT = False
            if hasattr(request, 'client') and not isinstance(request.client, AnonymousUser):
                marketplace = request.client.marketplace
                IS_CLIENT = True
            else:
                marketplace = request.user.marketplace
            produit_data['marketplace'] = marketplace.id_marketplace
            serializer = ProduitSerializer(data=produit_data)
            if serializer.is_valid():
                serializer.save()
                for image in images:
                    ImageProduit.objects.create(image=image, produit=serializer.data['id_produit'])
                MARKET_SELLING_NOTE = int(os.getenv('MARKET_SELLING_NOTE'))
                if IS_CLIENT:
                    client = request.client 
                    client.credit_vert += MARKET_SELLING_NOTE
                    client.save()
                else:
                    request.user.credit_vert += MARKET_SELLING_NOTE
                    request.user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProduitAchatView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]
    
    def validate_data(self, data):
        try:
            keys = ['produit']
            if any(key not in data.keys()for key in keys):return False
            return data['produit'].isnumeric and Produit.objects.filter(id_produit=int(data['produit'])).exists()
        except Exception:
            return False

    def post(self, request):
        try:
            # request.data = ['produit']
            WITH_PAYMENT_MONEY = bool(os.getenv("WITH_PAYMENT_MONEY"))
            if not self.validate_data(request.data):
                return Response({'erreur':'Veuillez verifier les informations fournies'}, status=status.HTTP_400_BAD_REQUEST)
            produit_id = request.data.get('produit')
            produit = get_object_or_404(Produit, id_produit=produit_id)
            if hasattr(request, 'client') and not isinstance(request.client, AnonymousUser):
                client = request.client
                if client == produit.marketplace.vendeur:
                    return Response({'erreur':'Vous ne pouvez pas acheter vos produits'}, status=status.HTTP_401_UNAUTHORIZED)
                if WITH_PAYMENT_MONEY:
                    if client.vouchers.amount < produit.price:
                        return Response({'erreur':'Votre solde est insuffisant pour cette opération'}, status=status.HTTP_400_BAD_REQUEST)
                achat = client.new_achat(produit)
                MARKET_BUYING_NOTE = int(os.getenv('MARKET_BUYING_NOTE'))
                client.credit_vert += MARKET_BUYING_NOTE
                client.save()
            elif hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                user = request.user
                if user == produit.marketplace.vendeur:
                    return Response({'erreur':'Vous ne pouvez pas acheter vos produits'}, status=status.HTTP_401_UNAUTHORIZED)
                if WITH_PAYMENT_MONEY:
                    if user.vouchers.amount < produit.price:
                        return Response({'erreur':'Votre solde est insuffisant pour cette opération'}, status=status.HTTP_400_BAD_REQUEST)
                achat = user.new_achat(produit)
                user.credit_vert += MARKET_BUYING_NOTE
                user.save()
            else:
                return Response({'erreur': 'Acheteur non identifié'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'message': 'Achat réalisé avec succès',
                'produit': ProduitSerializer(produit).data,
                'achat': AchatProduitSerializer(achat).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)