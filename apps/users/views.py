from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers import UserSerializer, LoginSerializer, RegisterSerializer

from dotenv import load_dotenv
from config import settings

import os
from datetime import datetime

load_dotenv()


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        user = serializer.data
        if not user['is_active']:
            return Response({'error': 'Accès refusé: votre compte doit être actif. Veuillez vous connecter pour continuer.'}, status=403)
        return Response(user, status=200)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request:Request):
        try:
            user = User.objects.get(id=request.user.id)
            user.is_active = False
            user.save()
            return Response({'message':'Utilisateur déconnecté avec succès.'}, status=200)
        except User.DoesNotExist:
            return Response({'erreur':message('user',404)}, status=404)

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        # request.data.keys = ['email', 'password']
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def check_if_user_exist(self, email):
        return User.objects.filter(email=email).exists()
    
    def Superuser_exist(self):
        return User.objects.all().exists()
    
    def post(self, request):
        # request.data.keys = ['first_name','last_name','email','password','contact', 'sexe', 'domaine', 'proffession', 'organisation']
        try:
            if self.check_if_user_exist(request.data['email']):
                return Response({'erreur':'email existant'},status=400)
            if self.Superuser_exist():
                return Response({'erreur':'Action non autorisé'},status=401)
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = User.objects.get(email=serializer.data['email'])
                return Response({'email':user.email, 'password':user.password}, status=status.HTTP_201_CREATED)
            else:
                return Response({'erreur':'erreur de serialisation'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)