from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.sante.models import Woman, Menstruation, Ovulation, Symptom
from apps.sante.serializers import WomanSerializer, MenstruationSerializer, OvulationSerializer, SymptomSerializer
from apps.sante.permissions import IsAuthenticatedWoman

from config.helpers.authentications import UserOrClientAuthentication

from datetime import timedelta
import traceback


class MenstruationListView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request):
        try:
            menstruations = Menstruation.objects.filter(woman=request.woman)
            serializer = MenstruationSerializer(menstruations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Menstruation.DoesNotExist:
            return Response({'detail': 'Menstruation records not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MenstruationNew(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def post(self, request):
        # request.data = ['start_date', 'end_date']
        try:
            serializer = MenstruationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(woman=request.woman)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MenstruationPredictView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request):
        try:
            last_menstruation = request.woman.menstruations.last()
            if not last_menstruation:
                return Response({'detail': 'No menstruation data available for prediction'}, status=status.HTTP_404_NOT_FOUND)
            
            predicted_start = last_menstruation.end_date + timedelta(days=request.woman.average_cycle_length)
            return Response({'predicted_start_date': predicted_start}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class OvulationPredictView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request):
        try:
            last_period = request.woman.last_period_date
            if not last_period:
                return Response({'detail': 'Last period date not available'}, status=status.HTTP_404_NOT_FOUND)
            
            predicted_ovulation_date = last_period + timedelta(days=request.woman.average_cycle_length - 14)
            fertility_window_start = predicted_ovulation_date - timedelta(days=5)
            fertility_window_end = predicted_ovulation_date + timedelta(days=1)
            return Response({
                'predicted_ovulation_date': predicted_ovulation_date,
                'fertility_window_start': fertility_window_start,
                'fertility_window_end': fertility_window_end
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class WomanSymptomsNewView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def post(self, request):
        try:
            serializer = SymptomSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(woman=request.woman)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class WomanSymptomListView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request):
        try:
            symptoms = Symptom.objects.filter(woman=request.woman)
            serializer = SymptomSerializer(symptoms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)