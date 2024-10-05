from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.conf import settings

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import PasswordField
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, timedelta
from django.utils import timezone
from uuid import uuid4

from config.helpers.helper import is_token_blacklisted, get_timezone
from apps.client.tokens import ClientRefreshToken
from apps.client.models import Client



class ClientSerializer(serializers.ModelSerializer):
    profile_url = serializers.SerializerMethodField()
    adress = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'contact', 'adress', 'sexe', 'profile_url', 'last_login', 'joined_at']

    def get_adress(self, obj):
        return obj.adress
    
    def update(self, instance, validate_data):
        if 'password' in validate_data:
            validate_data['password'] = make_password(validate_data.get('password'))
        return super(ClientSerializer, self).update(instance, validate_data)

    def get_profile_url(self, obj):
        return f"{settings.BASE_URL}api/client{obj.profile.url}" if obj.profile else None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        all_detail = self.context.get("all_detail", False)
        return representation

class LoginClientSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = PasswordField()

    def authenticate(self, email, password):
        try:
            client = Client.objects.get(email=email)
            if check_password(password, client.password):
                return client
            else:
                return None
        except Client.DoesNotExist:
            return None

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        client = self.authenticate(email=email, password=password)

        if not client:
            raise AuthenticationFailed('Identifiants incorrects.')
        if not client.is_email_verified:
            raise AuthenticationFailed('E-mail non vérifié.')
        
        client.is_active = True
        client.last_login = timezone.now()
        client.save()

        data = {}
        refresh = self.get_token_for_client(client)
        data['access'] = str(refresh.access_token)
        data['name'] = client.name
        return data
    
    def get_token_for_client(self, client):
        return ClientRefreshToken.for_client(client)

class RegisterClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Client
        fields = ['email', 'password', 'name', 'contact', 'adress', 'sexe']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        hashed_password = make_password(validated_data['password'])

        client = Client.objects.create(
            name=validated_data['name'].capitalize(),
            email=validated_data['email'],
            contact=validated_data['contact'],
            adress=validated_data['adress'],
            password=hashed_password,
            sexe=validated_data.get('sexe', 'I')
        )
        
        client.save()
        
        client_data = ClientSerializer(client).data
        data = {
            'email': client_data['email']
        }
        return data