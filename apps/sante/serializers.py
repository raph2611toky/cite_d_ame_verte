from rest_framework import serializers
from .models import Woman, Menstruation, Ovulation, Symptom, Notification

from datetime import timedelta

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
        last_info = self.context.get('last_info', False)
        representation = super().to_representation(instance)
        if only_menstruations:
            representation.pop('ovulations', None)
            representation.pop('symptoms', None)
        if last_info:
            representation['ovulation_predict'] = OvulationSerializer(instance.ovulations.last()).data
            last_menstruation = instance.menstruations.last()
            predicted_start = last_menstruation.start_date + timedelta(days=instance.average_cycle_length)
            predicted_end = predicted_start + timedelta(days=instance.average_menstruation_duration)
            representation['menstruation_predict'] = {
                "start_date": predicted_start,
                "end_date": predicted_end
            }
            representation['menstruation_last'] = MenstruationSerializer(last_menstruation).data
            representation.pop('ovulations', None)
            representation.pop('mensturations', None)
        return representation


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id_notification', 'message', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y")