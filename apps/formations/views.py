from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import AnonymousUser

from config.helpers.authentications import UserOrClientAuthentication
from config.helpers.permissions import IsAuthenticatedUserOrClient
from apps.client.permissions import IsAuthenticatedClient
from apps.client.models import Client
from django.utils import timezone

from apps.formations.models import Formation, FormationPayment, FileFormationSession, FormationSession
from apps.formations.serializers import FormationSerializer, FormationPaymentSerializer, ClientFormationSubscriptionSerializer, FormationSessionSerializer

from dotenv import load_dotenv
from datetime import timedelta
import traceback
import os
import json

load_dotenv()

class FormationListView(APIView):
    authentication_classes = [UserOrClientAuthentication]
    permission_classes = [IsAuthenticatedUserOrClient]

    def get(self, request):
        try:
            formations = Formation.objects.all().order_by('-id_formation')
            if hasattr(request, 'client') and not isinstance(request.client, AnonymousUser):
                serializer = FormationSerializer(formations, many=True, context={'permit_to_see_sessions':True, 'client':request.client})
            elif hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                serializer = FormationSerializer(formations, many=True, context={'permit_to_see_sessions':True, 'user': request.user})
            else:
                return Response({'erreur':'Utilisateur non identifié'}, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FormationFilterView(APIView):
    authentication_classes = [UserOrClientAuthentication]
    permission_classes = [IsAuthenticatedUserOrClient]

    def get(self, request):
        try:
            if hasattr(request, 'client') and not isinstance(request.client, AnonymousUser):
                formations = request.client.formations.order_by('-id_formation')
                serializer = FormationSerializer(formations, many=True,context={'permit_to_see_sessions':True, 'client':request.client})
            elif hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                formations = request.user.formations.order_by('-id_formation')
                serializer = FormationSerializer(formations, many=True,context={'permit_to_see_sessions':True,'user':request.user})
            else:
                return Response({'erreur': 'Personne non identifié'}, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FormationProfileFindView(APIView):
    authentication_classes = [UserOrClientAuthentication]
    permission_classes = [IsAuthenticatedUserOrClient]

    def get(self, request, id_formation):
        try:
            formation = Formation.objects.get(id_formation=id_formation)
            serializer = FormationSerializer(formation, {'permit_to_see_sessions':True,'client':request.client if request.client.id else request.user})
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
                if any(key not in data['payment'].keys()for key in payment_keys):
                    return False
            return data['payment']['price'] > 0
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
                user = request.user
                formation_save = serializer.save()
                formation = Formation.objects.get(id_formation=formation_save.id_formation)
                formation.organisateurs.add(user.id)
                if not formation.is_free:
                    payment_data = request.data.get('payment')
                    if payment_data:
                        payment_serializer = FormationPaymentSerializer(data=json.loads(payment_data))
                        if payment_serializer.is_valid():
                            payment_serializer.save(formation=formation, organiser=user)
                        else:
                            return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                FORMATION_NOTE = int(os.getenv('FORMATION_NOTE'))
                user.credit_vert += FORMATION_NOTE
                user.save()
                formation.save()
                return Response(FormationSerializer(formation).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
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
    
    def validate_payment_mobile(self,formation:Formation, client:Client):
        try:
            if formation.is_free:
                return True
            formation_payments = formation.payments.all()
            if formation_payments.count() < 1:
                return False
            formation_payment = formation_payments.last()
            if formation_payment.price > client.vouchers.amount:
                return False
            return True
        except Exception:
            return False
    
    def validate_data(self, data):
        try:
            keys = ['formation']
            if any(key not in data.keys()for key in keys):
                return False
            return Formation.objects.filter(id_formation=data['formation']).exists()
        except Exception as e:
            return False
    
    def post(self, request):
        # request.data = ['fomation']
        try:
            WITH_PAYMENT_MONEY = bool(os.getenv("WITH_PAYMENT_MONEY"))
            if not self.validate_data(request.data):
                return Response({'erreur', 'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            client = request.client
            formation_id = request.data.get('formation')
            if not formation_id:
                return Response({"error": "Formation payment ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            formation = Formation.objects.get(id_formation=formation_id)
            formation_payment = formation.payments.all()
            FORMATION_NOTE = int(os.getenv('FORMATION_NOTE'))
            if WITH_PAYMENT_MONEY:
                if not self.validate_payment_mobile(formation, client):
                    return Response({'erreur':'Votre solde n\'est pas suffisant pour cette opération'}, status=status.HTTP_400_BAD_REQUEST)
            if formation_payment.count() < 1 and not formation.is_free:
                return Response({'erreur': 'Formation has no payments.'}, status=status.HTTP_400_BAD_REQUEST)
            elif not formation.is_free:
                start_date = timezone.now()
                formation_payment = formation_payment.last()
                end_date = timezone.now() + timedelta(days=formation_payment.validity_days)
                subscription_data = {
                    'client': client.id,
                    'formation_payment': formation_payment,
                    'start_date': start_date,#.strftime('%Y-%m-%d'),
                    'end_date': end_date,#.strftime('%Y-%m-%d')
                }
                serializer = ClientFormationSubscriptionSerializer(data=subscription_data, context=subscription_data)
                if serializer.is_valid():
                    serializer.save()
                    if not client in formation.participants.all():
                        client.credit_vert += FORMATION_NOTE
                        client.save()
                        if WITH_PAYMENT_MONEY:
                            formation_price = formation_payment.price
                            client.soustract_voucher(formation_price)
                            user = formation.organisateurs.all().first()
                            user.add_voucher(formation_price)
                    formation.participants.add(request.client)
                    formation.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            elif formation.is_free:
                formation.participants.add(request.client)
                formation.save()
                if not client in formation.participants.all():
                    client.credit_vert += FORMATION_NOTE
                    client.save()
                return Response({'message':"Souscription reussi"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class FormationSessionFindView(APIView):
    permission_classes = [IsAuthenticatedUserOrClient]
    authentication_classes = [UserOrClientAuthentication]
    
    def get(self, request, id_formationsession):
        try:
            if hasattr(request, 'client') and not isinstance(request.client, AnonymousUser):
                client = request.client
                formation_sessions = FormationSession.objects.filter(formation__participants=client.id)
                formation_session = FormationSession.objects.get(id_formationsession=id_formationsession)
                if formation_session not in formation_sessions:
                    return Response({'erreur': 'Vous n\'avez pas l\'autorisation de consulter cette information'}, status=status.HTTP_401_UNAUTHORIZED)
            elif hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                user = request.user
                formation_sessions = FormationSession.objects.filter(formation__organisateurs=user.id)
                formation_session = FormationSession.objects.get(id_formationsession=id_formationsession)
                if formation_session not in formation_sessions:
                    return Response({'erreur': 'Vous n\'avez pas l\'autorisation de consulter cette information'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'erreur': 'Information d\'utilisateur non fournie'}, status=status.HTTP_403_FORBIDDEN)
            formationsession = FormationSessionSerializer(formation_session).data
            return Response(formationsession, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FormationSessionNewView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def validate_data(self, data):
        try:
            keys = ['description', 'formation']
            if any(key not in data.keys()for key in keys):
                return False
            return Formation.objects.filter(id_formation=data['formation']).exists()
        except Exception:
            return False
    
    def post(self, request):
        try:
            # request.FILES = ['files']
            # request.data = ['formation','description', 'is_online'=False]
            if not self.validate_data(request.data):
                return Response({'erreur': 'Tous les champs sont requist'}, status=status.HTTP_400_BAD_REQUEST)
            files = request.FILES.getlist('files')
            formation = Formation.objects.get(id_formation=request.data['formation'])
            if request.user not in formation.organisateurs.all():
                return Response({'erreur':'Vous n\'avez pas l\'autorisation de faire cette action'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = FormationSessionSerializer(data=request.data)
            if serializer.is_valid():
                formation_session_save = serializer.save(formation=formation)
                for file in files:
                    FileFormationSession.objects.create(file=file, formation_session=formation_session_save)
                return Response({'message':'Session successfully added'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class FormationSessionProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id_formationsession):
        try:
            formationsession = FormationSession.objects.get(id_formationsession=id_formationsession)
            formation_sessions = FormationSession.objects.filter(formation__organisateurs=request.user.id)
            if formationsession not in formation_sessions:
                return Response({'erreur':'Vous n\'avez pas l\'autorisation de faire cette action'}, status=status.HTTP_401_UNAUTHORIZED)
            formationsession.delete()
            return Response({'message':'formation session a été supprimé avec succès.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)
