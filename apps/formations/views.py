from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from config.helpers.authentications import UserOrClientAuthentication
from config.helpers.permissions import IsAuthenticatedUserOrClient
from apps.client.permissions import IsAuthenticatedClient

from apps.formations.models import Formation, FormationPayment
from apps.formations.serializers import FormationSerializer, FormationPaymentSerializer


class FormationListView(APIView):
    authentication_classes = [UserOrClientAuthentication]
    permission_classes = [IsAuthenticatedUserOrClient]

    def get(self, request):
        try:
            formations = Formation.objects.all()
            serializer = FormationSerializer(formations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FormationProfileFindView(APIView):
    authentication_classes = [UserOrClientAuthentication]
    permission_classes = [IsAuthenticatedUserOrClient]

    def get(self, request, id_formation):
        try:
            formation = Formation.objects.get(id_formation=id_formation)
            serializer = FormationSerializer(formation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Formation.DoesNotExist:
            return Response({"error": "Formation not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FormationProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id_formation):
        try:
            formation = Formation.objects.get(id_formation=id_formation)
            if request.user not in formation.organisateurs.all():
                return Response({'erreur': 'Vous n\'avez pas l\'authorisation de faire cette action.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FormationSerializer(formation, data=request.data, partial=True)
            if serializer.is_valid():
                formation_serializer = serializer.save()

                if not formation.is_free:
                    payment_data = request.data.get('payment')
                    if payment_data:
                        if hasattr(formation, 'payments') and formation.payments.exists():
                            payment = formation.payments.first()
                            payment_serializer = FormationPaymentSerializer(payment, data=payment_data, partial=True)
                        else:
                            payment_serializer = FormationPaymentSerializer(data=payment_data)

                        if payment_serializer.is_valid():
                            payment_serializer.save(formation=formation, organiser=request.user)
                        else:
                            return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response(formation_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Formation.DoesNotExist:
            return Response({"error": "Formation not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id_formation, *args, **kwargs):
        try:
            formation = Formation.objects.get(id_formation=id_formation)
            formation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Formation.DoesNotExist:
            return Response({"error": "Formation not found"}, status=status.HTTP_404_NOT_FOUND)


class FormationNewView(APIView):
    permission_classes = [IsAuthenticated]
    
    def validate_data(self, data):
        try:
            keys = ['name_formation', 'description_formation', 'domaine', 'is_free']
            if not data['is_free']:
                keys += ['payment']
            if any(key not in data.keys()for key in keys):
                return False
            if not data['is_free']:
                payment_keys = ['price', 'validity_days']
                if any(key not in data['is_free'].keys()for key in payment_keys):
                    return False
            return True
        except Exception as e:
            return False

    def post(self, request):
        # request.data = ['name_formation', 'description_formation', 'domaine', 'is_free']
        # request.data['payment'] = ['price', 'validity_days']
        try:
            if not self.validate_data(request.data):
                return Response({'erreur':'tous les attributs sont requis.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FormationSerializer(data=request.data)
            if serializer.is_valid():
                formation_save = serializer.save()
                formation = Formation.objects.get(id_formtion=formation_save.id_formation)
                formation.organisateurs.add(request.user.id)
                if not formation.is_free:
                    payment_data = request.data.get('payment')
                    if payment_data:
                        payment_serializer = FormationPaymentSerializer(data=payment_data)
                        if payment_serializer.is_valid():
                            payment_serializer.save(formation=formation, organiser=request.user)
                        else:
                            return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                formation.save()
                return Response(FormationSerializer(formation).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FormationPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # request.data = ['formation', 'price', 'validity_days']
        formationpayment_data = request.data.copy()
        formationpayment_data['organiser'] = request.user.id
        serializer = FormationPaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormationSubscription(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []
    
    def post(self, request):
        try:
            client = request.user
            formation_payment_id = request.data.get('formation_payment')
            if not formation_payment_id:
                return Response({"error": "Formation payment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                formation_payment = FormationPayment.objects.get(id=formation_payment_id)
            except FormationPayment.DoesNotExist:
                return Response({"error": "Formation payment not found."}, status=status.HTTP_404_NOT_FOUND)

            subscription_data = {
                'client': client.id,
                'formation_payment': formation_payment.id
            }
            serializer = ClientFormationSubscriptionSerializer(data=subscription_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)