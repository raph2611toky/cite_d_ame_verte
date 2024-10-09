from rest_framework import serializers

from apps.formations.models import Formation, FormationPayment, ClientFormationSubscription
from apps.client.models import Client

class FormationPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationPayment
        fields = ['formation', 'organiser', 'price', 'validity_days']

class ClientFormationSubscriptionSerializer(serializers.ModelSerializer):
    formation_payment = FormationPaymentSerializer()

    class Meta:
        model = ClientFormationSubscription
        fields = ['client', 'formation_payment', 'start_date', 'end_date']

class FormationSerializer(serializers.ModelSerializer):
    payments = FormationPaymentSerializer(many=True, read_only=True)
    participants = serializers.StringRelatedField(many=True)

    class Meta:
        model = Formation
        fields = ['id_formation', 'name_formation', 'description_formation', 'domaine', 'is_free', 'organisateurs', 'participants', 'created_at', 'payments']
