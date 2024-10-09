from rest_framework import serializers

from apps.formations.models import Formation, FormationPayment, ClientFormationSubscription, FileFormationSession, FormationSession
from apps.client.models import Client

from django.conf import settings

class FormationPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationPayment
        fields = ['formation', 'organiser', 'price', 'validity_days']

class ClientFormationSubscriptionSerializer(serializers.ModelSerializer):
    formation_payment = FormationPaymentSerializer(read_only=True)

    class Meta:
        model = ClientFormationSubscription
        fields = ['client', 'formation_payment', 'start_date', 'end_date']

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
        fields = ['id_formationsession', 'description', 'files', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')

class FormationSerializer(serializers.ModelSerializer):
    payments = FormationPaymentSerializer(many=True, read_only=True)
    participants = serializers.StringRelatedField(many=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Formation
        fields = ['id_formation', 'name_formation', 'description_formation', 'domaine', 'is_free', 'organisateurs', 'participants', 'created_at', 'payments']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y')
