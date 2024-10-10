from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.sante.models import Woman, Menstruation, Ovulation, Symptom, Notification
from apps.sante.serializers import WomanSerializer, MenstruationSerializer, OvulationSerializer, SymptomSerializer
from apps.sante.permissions import IsAuthenticatedWoman

from config.helpers.authentications import UserOrClientAuthentication

from datetime import timedelta, datetime
import traceback


class WomanInfoView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request):
        try:
            woman = WomanSerializer(request.woman).data
            return Response(woman, status=status.HTTP_200_OK)
        except Menstruation.DoesNotExist:
            return Response({'detail': 'Menstruation records not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MenstruationListView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def get(self, request):
        try:
            woman = WomanSerializer(request.woman, context={'only_menstruations':True}).data
            return Response(woman, status=status.HTTP_200_OK)
        except Menstruation.DoesNotExist:
            return Response({'detail': 'Menstruation records not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MenstruationNew(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    # request.data.keys = ['start_date']
    def post(self, request):
        try:
            woman = request.woman
            start_date = datetime.strptime(request.data['start_date'], '%Y-%m-%d').date()
            last_menstruation = woman.menstruations.last()

            if last_menstruation:
                last_menstruation.end_date = start_date
                last_menstruation.cycle_length = (start_date - last_menstruation.start_date).days
                last_menstruation.save()

            
            data = {
                'start_date': start_date
            }

            serializer = MenstruationSerializer(data=data)
            if serializer.is_valid():
                menstruation = serializer.save(woman=woman)
                woman.last_period_date = start_date
                woman.save()
                
                woman.update_average_cycle_length()
                
                predicted_ovulation_date = start_date + timedelta(days=woman.average_cycle_length - 14)
                fertility_window_start = predicted_ovulation_date - timedelta(days=5)
                fertility_window_end = predicted_ovulation_date + timedelta(days=1)
                
                Ovulation.objects.create(
                    woman=woman,
                    predicted_ovulation_date=predicted_ovulation_date,
                    fertility_window_start=fertility_window_start,
                    fertility_window_end=fertility_window_end
                )
                
                if woman.notification_preference:
                    Notification.objects.create(
                        woman=woman,
                        message=f"Une nouvelle menstruation a été ajoutée pour la période du {menstruation.start_date} au {menstruation.end_date}."
                    )
                    
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WomanConfigureView(APIView):
    permission_classes = [IsAuthenticatedWoman]
    authentication_classes = [UserOrClientAuthentication]

    def post(self, request):
        try:
            # request.data = ['notification_preference']
            preference = request.data.get('notification_preference', None)
            if preference is None:
                return Response({'error': 'Le champ notification_preference est requis'}, status=status.HTTP_400_BAD_REQUEST)

            request.woman.notification_preference = preference
            request.woman.save()

            return Response({'message': 'Préférence de notification mise à jour avec succès'}, status=status.HTTP_200_OK)
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
            
            predicted_start = last_menstruation.start_date + timedelta(days=request.woman.average_cycle_length)
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
    
    def validate_data(self, data):
        try:
            keys = ['date', 'description']
            if any(key not in data.keys()for key in keys):
                return False
            return True
        except Exception:
            return False

    def post(self, request):
        try:
            # request.data = ['date', 'description']
            if not self.validate_data(request.data):
                return Response({'erreur':'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            symptom_data = request.data
            symptom_data['date'] = datetime.strptime(request.data['date'], "%Y-%m-%d").date()
            serializer = SymptomSerializer(data=symptom_data, context=symptom_data)
            if serializer.is_valid():
                serializer.save(woman=request.woman)
                return Response({'message':'symptom soumis avec succès'}, status=status.HTTP_201_CREATED)
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