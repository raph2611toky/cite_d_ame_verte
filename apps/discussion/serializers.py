from rest_framework import serializers

from apps.discussion.models import PlanningFamiliale, FilePlanningFamiliale, FileMessage, Message, Discussion
from apps.medical.serializers import DoctorSerializer
from apps.client.serializers import ClientSerializer
from django.conf import settings


class FilePlanningFamilialeSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = FilePlanningFamiliale
        fields = ['id_file_pf', 'file_url', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    
    def get_file_url(self,obj):
        return f'{settings.BASE_URL}api{obj.file.url}' if obj.file else None
    
class PlanningFamilialeSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    files = FilePlanningFamilialeSerializer(read_only=True, many=True)
    
    class Meta:
        model = PlanningFamiliale
        fields = ['id_pf', 'description', 'titre', 'files', 'sender', 'created_at']
           
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    
class FileMessageSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = FileMessage
        fields = ['id_file', 'file_url', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    
    def get_file_url(self,obj):
        return f'{settings.BASE_URL}api{obj.file.url}' if obj.file else None
    
class MessageSerializer(serializers.ModelSerializer):
    files = FileMessageSerializer(read_only=True, many=True)
    
    class Meta:
        model = Message
        fields = ['id_message', 'contenu', 'discussion', 'sender', 'files', 'created_at']
    
class DiscussionSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    doctors = DoctorSerializer(many=True, read_only=True)
    clients = ClientSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = ['id_discussion', 'doctors', 'clients', 'messages', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    
    def get_messages(self, obj):
        return FileMessageSerializer(obj.messages.all(), many=True).data