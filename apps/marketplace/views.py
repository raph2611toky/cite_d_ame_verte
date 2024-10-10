from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView

from apps.marketplace.models import Produit, MarketPlace
from apps.marketplace.serializers import ProduitSerializer, AchatProduitSerializer

from config.helpers.permissions import IsAuthenticatedUserOrClient
from config.helpers.authentications import UserOrClientAuthentication

import traceback

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
        try:
            if not self.validate_data(request.data):
                return Response({'erreur':'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            produit_data = request.data
            if hasattr(request, 'client'):
                marketplace = request.client.marketplace
            else:
                marketplace = request.user.marketplace
            produit_data['marketplace'] = marketplace.id_marketplace
            serializer = ProduitSerializer(data=produit_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProduitAchatView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]

    def post(self, request):
        try:
            # request.data = ['produit']
            produit_id = request.data.get('produit')
            produit = get_object_or_404(Produit, id_produit=produit_id)

            if hasattr(request, 'client'):
                client = request.client
                achat = client.new_achat(produit)
            elif hasattr(request, 'user'):
                user = request.user
                achat = user.new_achat(produit)
            else:
                return Response({'erreur': 'Acheteur non identifié'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'message': 'Achat réalisé avec succès',
                'produit': ProduitSerializer(produit).data,
                'achat': AchatProduitSerializer(achat).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)