from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.discussion.serializers import DiscussionSerializer, MessageSerializer, PlanningFamilialeSerializer
from apps.discussion.models import Discussion, Message, PlanningFamiliale
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
            # request.data = ['description','titre']
            pass
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)