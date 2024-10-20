from rest_framework import serializers
from django.conf import settings

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import PasswordField
from django.contrib.auth.hashers import check_password, make_password

from config.helpers.helper import get_timezone
from apps.client.tokens import ClientRefreshToken
from apps.client.models import Client, DepositVoucherClient, DepotClient, QueuePaymentVerificationClient


class ClientSerializer(serializers.ModelSerializer):
    profile_url = serializers.SerializerMethodField()
    adress = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'contact', 'adress', 'sexe', 'profile_url', 'is_active', 'last_login', 'joined_at']

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
        client.is_active = True
        client.last_login = get_timezone()
        client.save()

        data = {}
        refresh = self.get_token_for_client(client)
        data['access'] = str(refresh.access_token)
        data['name'] = client.first_name + ' ' + client.last_name
        data['sexe'] = client.sexe
        return data
    
    def get_token_for_client(self, client):
        return ClientRefreshToken.for_client(client)

class RegisterClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Client
        fields = ['email', 'password', 'first_name', 'last_name', 'contact', 'adress', 'sexe']

    def validate(self, attrs):
        self.create(attrs)
        return attrs

    def create(self, validated_data):
        hashed_password = make_password(validated_data['password'])
        client = Client.objects.create(
            first_name=validated_data['first_name'].capitalize(),
            last_name=validated_data['last_name'],
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
    
class QueuePaymentVerificationClientSerializer(serializers.ModelSerializer):
    modified_at = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = QueuePaymentVerificationClient
        fields = ["id_queuepayement", "client",'numero_source', 'reference', 'date_payement', 'mode_payement', 'status', "created_at", "modified_at"]
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y, %H:%M:%S")
    
    def get_modified_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y, %H:%M:%S")

class DepotClientSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = DepotClient
        fields = ['id_depot', 'client', 'numero_source', 'reference', 'date_payement', 'mode_payement', 'solde', 'currency', 'status', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y, %H:%M:%S")

class DepositVoucherClientSerializer(serializers.ModelSerializer):
    date_created = serializers.SerializerMethodField()
    modified_at = serializers.SerializerMethodField()
    
    class Meta:
        model = DepositVoucherClient
        fields = ['id_depositvoucher', 'client', 'amount', 'date_created', 'is_active', 'modified_at']
        
    def get_date_created(self, obj):
        return obj.date_created.strftime("%d-%m-%Y")
    
    def get_modified_at(self, obj):
        return obj.modified_at.strftime("%d-%m-%Y")