from rest_framework import serializers

from apps.formations.models import Formation, FormationPayment, ClientFormationSubscription, FileFormationSession, FormationSession
from apps.client.models import Client
from apps.users.models import User
from apps.client.serializers import ClientSerializer
from apps.users.serializers import UserSerializer

from django.conf import settings

class FormationPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationPayment
        fields = ['price', 'validity_days']

class ClientFormationSubscriptionSerializer(serializers.ModelSerializer):
    formation_payment = FormationPaymentSerializer(read_only=True)
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = ClientFormationSubscription
        fields = [ 'client', 'formation_payment', 'start_date', 'end_date']
        
    def validate(self, attrs):
        attrs = self.context
        attrs['client'] = Client.objects.get(id=attrs['client'])
        return attrs
    
    def get_start_date(self, obj):
        return obj.start_date.strftime('%d-%m-%Y')
    
    def get_end_date(self, obj):
        return obj.end_date.strftime('%d-%m-%Y')

class FileFormationSessionSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    class Meta:
        model = FileFormationSession
        fields = ['id_file_session','file_url']
        
    def get_file_url(self, obj):
        return f'{settings.BASE_URL}api{obj.file.url}' if obj.file else None
    
class FormationSessionSerializer(serializers.ModelSerializer):
    files = FileFormationSessionSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = FormationSession
        fields = ['id_formationsession', 'formation', 'description', 'titre', 'is_online', 'files', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')

class FormationSerializer(serializers.ModelSerializer):
    payments = FormationPaymentSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    organisateurs = ClientSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Formation
        fields = ['id_formation', 'name_formation', 'description_formation', 'domaine', 'is_free', 'organisateurs', 'participants', 'created_at', 'payments']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')

    def create(self, validated_data):
        return super().create(validated_data)
    
    def to_representation(self, instance):
        permit_to_see_sessions = self.context.get('permit_to_see_sessions',None)
        representation = super().to_representation(instance)
        if not permit_to_see_sessions is None:
            if isinstance(permit_to_see_sessions, Client):
                client = permit_to_see_sessions
                if client in instance.participants.all():
                    representation['sessions'] = FormationSessionSerializer(instance.sessions, many=True).data
            elif isinstance(permit_to_see_sessions, User):
                user = permit_to_see_sessions
                if user in instance.organisateurs.all():
                    representation['sessions'] = FormationSessionSerializer(instance.sessions, many=True).data
        return representation