from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import PasswordField

from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    profile_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'contact', 'sexe', 'domaine', 'profession', 'organisation', 'profile_url', 'is_active', 'last_login', 'date_joined']

    def get_name(self,obj):
        return obj.first_name.capitalize() + ' ' + obj.last_name.capitalize()
    
    def update(self, instance, validate_data):
        if 'password' in validate_data:
            validate_data['password'] = make_password(validate_data.get('password'))
        return super(UserSerializer, self).update(instance, validate_data)

    def get_profile_url(self, obj):
        return f"{settings.BASE_URL}api{obj.profile.url}" if obj.profile else None

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = PasswordField()
    
    def validate(self, attrs):
        users = authenticate(**attrs)
        if not users:
            raise AuthenticationFailed()
        users_logged = User.objects.get(id=users.id)
        users_logged.is_active = True
        update_last_login(None, users_logged)
        users_logged.save()
        data = {}
        refresh = self.get_token(users_logged)
        data['access'] = str(refresh.access_token)
        data['name'] = users_logged.first_name+' '+users_logged.last_name
        return data
    
    def get_token(self, users):
        token = RefreshToken.for_user(users)
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'contact','sexe', 'domaine', 'profession', 'organisation']
        
    def validate(self, attrs):
        self.create(attrs)
        return attrs
        
    def create(self, validated_data):
        users = User.objects.create(
            first_name=validated_data['first_name'].capitalize(),
            last_name=validated_data['last_name'].capitalize(),
            email=validated_data['email'],
            contact=validated_data['contact'],
            sexe=validated_data.get('sexe','I')[0].upper(),
            domaine=validated_data['domaine'],
            profession=validated_data['profession'],
            organisation=validated_data['organisation'],
            is_superuser=False,
            is_staff=True
        )
        users.set_password(validated_data['password'])
        users.is_active = False
        users.save()
        users_created = User.objects.get(id=users.id)
        data = {
            'email': users_created.email
        }
        return data