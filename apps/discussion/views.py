from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType


from apps.discussion.serializers import DiscussionSerializer, MessageSerializer, PlanningFamilialeSerializer
from apps.discussion.models import Discussion, Message, PlanningFamiliale, FileMessage, FilePlanningFamiliale
from apps.medical.permissions import IsAuthenticatedWomanOrDoctor


class PlanningFamilialeListView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def get(self, request):
        try:
            planningFamiliales = PlanningFamilialeSerializer(PlanningFamiliale.objects.all(), many=True).data
            return Response(planningFamiliales)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PlanningFamilialeFilterView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def get(self, request):
        try:
            planningFamiliales = PlanningFamilialeSerializer(PlanningFamiliale.objects.filter(woman=request.woman), many=True).data
            return Response(planningFamiliales)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PlanningFamilialeNewView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def post(self, request):
        try:
            if request.is_woman:
                sender_type = ContentType.objects.get_for_model(request.woman.__class__)
                sender_id = request.user.id
            elif request.is_doctor:
                sender_type = ContentType.objects.get_for_model(request.user.__class__)
                sender_id = request.user.id
            else:
                return Response({'erreur': 'Utilisateur non autorisé'}, status=status.HTTP_403_FORBIDDEN)
            planning_familiale = PlanningFamiliale.objects.create(description=request.data['description'], titre=request.data['titre'], sender_id=sender_id, sender_type=sender_type)
            files = request.FILES.getlist('files')
            for file in files:
                FilePlanningFamiliale.objects.create(
                    file=file,
                    planning_familiale=planning_familiale
                )
            return Response({'message':'planning familiale soumis avec succès'})
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PlanningFamilialeDeleteView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def delete(self, request, pk):
        try:
            discussion = Discussion.objects.get(id_discussion=pk)
            discussion.delete()
            return Response({"message": "Discussion supprimée avec succès"}, status=status.HTTP_200_OK)
        except Discussion.DoesNotExist:
            return Response({"erreur": "Discussion non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DiscussionListView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def get(self, request):
        try:
            discussions = DiscussionSerializer(Discussion.objects.all(), many=True).data
            return Response(discussions)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DiscussionFilterView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def get(self, request):
        try:
            member_type = None
            if request.is_woman:
                member_type = ContentType.get_for_model(request.woman)
                member_id = request.woman.id
            elif request.is_doctor:
                member_type = ContentType.get_for_model(request.woman)
                member_id = request.doctor
            else:
                return Response({'erreur':'Personne non identifé'}, status=status.HTTP_400_BAD_REQUEST)
            discussions = DiscussionSerializer(Discussion.objects.filter(members_id=member_id, member_type=member_type), many=True).data
            return Response(discussions)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DiscussionNewView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def post(self, request):
        try:
            if request.is_woman:
                members_type = ContentType.objects.get_for_model(request.woman.__class__)
                members_id = request.user.id
            elif request.is_doctor:
                members_type = ContentType.objects.get_for_model(request.user.__class__)
                members_id = request.user.id
            else:
                return Response({'erreur': 'Utilisateur non autorisé'}, status=status.HTTP_403_FORBIDDEN)
            
            discussion = Discussion.objects.create(
                type=request.data.get('type'),
                members_id=members_id,
                members_type=members_type
            )
            return Response({'message': 'Discussion créée avec succès', 'discussion_id': discussion.id_discussion})
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DiscussionDeleteView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def delete(self, request, pk):
        try:
            discussion = Discussion.objects.get(id_discussion=pk)
            discussion.delete()
            return Response({"message": "Discussion supprimée avec succès"}, status=status.HTTP_200_OK)
        except Discussion.DoesNotExist:
            return Response({"erreur": "Discussion non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MessageNewView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def post(self, request):
        try:
            discussion_id = request.data.get('discussion')
            contenu = request.data.get('contenu')
            
            try:
                discussion = Discussion.objects.get(id_discussion=discussion_id)
            except Discussion.DoesNotExist:
                return Response({'erreur': 'Discussion non trouvée'}, status=status.HTTP_404_NOT_FOUND)
            
            if request.is_woman:
                sender_type = ContentType.objects.get_for_model(request.woman.__class__)
                sender_id = request.woman.id
            elif request.is_doctor:
                sender_type = ContentType.objects.get_for_model(request.user.__class__)
                sender_id = request.user.id
            else:
                return Response({'erreur': 'Utilisateur non autorisé'}, status=status.HTTP_403_FORBIDDEN)
            
            message = Message.objects.create(
                discussion=discussion,
                contenu=contenu,
                sender_type=sender_type,
                sender_id=sender_id
            )
            files = request.FILES.getlist('files')
            for file in files:
                FileMessage.objects.create(
                    file=file,
                    message=message
                )
            message_data = MessageSerializer(message).data
            return Response({'message': 'Message créé avec succès', 'data': message_data}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class FindOneDiscussionView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticatedWomanOrDoctor]
    
    def get(self, request, pk):
        try:
            discussion = Discussion.objects.get(id_discussion=pk)
            
            discussion_data = DiscussionSerializer(discussion).data
            return Response({'data': discussion_data}, status=status.HTTP_200_OK)
        
        except Discussion.DoesNotExist:
            return Response({'erreur': 'Discussion non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)