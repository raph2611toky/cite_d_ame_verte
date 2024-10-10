from rest_framework import serializers
from .models import Woman, Menstruation, Ovulation, Symptom, Notification

class MenstruationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menstruation
        fields = ['id_menstruation', 'start_date', 'end_date', 'cycle_length']

class OvulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ovulation
        fields = ['id_ovulation', 'predicted_ovulation_date', 'fertility_window_start', 'fertility_window_end']

class SymptomSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = Symptom
        fields = ['id_symptom', 'date', 'description']#, 'woman']

    def get_date(self, obj):
        return obj.date.strftime("%d-%m-%Y")
    
    def validate(self, attrs):
        attrs['date'] = self.context.get('date')
        return attrs

class WomanSerializer(serializers.ModelSerializer):
    menstruations = MenstruationSerializer(many=True, read_only=True)
    ovulations = OvulationSerializer(many=True, read_only=True)
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = Woman
        fields = ['id_woman', 'average_cycle_length', 'last_period_date', 'notification_preference', 'menstruations', 'ovulations', 'symptoms']
        
    def to_representation(self, instance):
        only_menstruations = self.context.get('only_menstruations',False)
        reprensetation = super().to_representation(instance)
        if only_menstruations:
            reprensetation.pop('ovulations', None)
            reprensetation.pop('symptoms', None)
        return reprensetation


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id_notification', 'message', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y")