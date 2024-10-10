from rest_framework import serializers
from .models import Woman, Menstruation, Ovulation, Symptom

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
        fields = ['id_symptom', 'date', 'description']

    def get_date(self, obj):
        return obj.date.strftime("%d-%m-%Y")

class WomanSerializer(serializers.ModelSerializer):
    menstruations = MenstruationSerializer(many=True, read_only=True)
    ovulations = OvulationSerializer(many=True, read_only=True)
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = Woman
        fields = ['id_woman', 'average_cycle_length', 'last_period_date', 'notification_preference', 'menstruations', 'ovulations', 'symptoms']
