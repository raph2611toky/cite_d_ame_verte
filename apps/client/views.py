from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import TokenError
from rest_framework.views import APIView

from apps.client.models import Client
from apps.client.permissions import IsAuthenticatedClient
from apps.client.serializers import ClientSerializer, LoginClientSerializer, RegisterClientSerializer

from dotenv import load_dotenv
from config import settings

import os
from datetime import datetime

load_dotenv()


class ProfileClientView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []

    def get(self, request):
        serializer = ClientSerializer(request.client, context={'request': request})
        client = serializer.data
        if not client['is_active']:
            return Response({'error': 'Accès refusé: votre compte doit être actif. Veuillez vous connecter pour continuer.'}, status=403)
        return Response(client, status=200)

class LogoutClientView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []

    def put(self, request:Request):
        try:
            client = Client.objects.get(id=request.client.id)
            client.is_active = False
            client.save()
            return Response({'message':'Utilisateur déconnecté avec succès.'}, status=200)
        except Client.DoesNotExist:
            return Response({'erreur':"Client non existant"}, status=404)

class LoginClientView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginClientSerializer

    def post(self, request):
        # request.data.keys = ['email', 'password']
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterClientView(APIView):
    permission_classes = [AllowAny]
    
    def check_if_client_exist(self, email):
        return Client.objects.filter(email=email).exists()
        
    def post(self, request):
        # request.data.keys = ['name','email','password','contact', 'sexe', 'adress']
        try:
            if self.check_if_client_exist(request.data['email']):
                return Response({'erreur':'email existant'},status=400)
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                client = Client.objects.get(email=serializer.data['email'])
                return Response({'email':client.email, 'password':client.password}, status=status.HTTP_201_CREATED)
            else:
                return Response({'erreur':'erreur de serialisation'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)