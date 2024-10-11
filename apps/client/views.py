from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import TokenError
from rest_framework.views import APIView

from apps.client.models import Client, TokenPairMobileAuthentication, DepositVoucherClient, DepotClient, QueuePaymentVerificationClient
from apps.users.models import User
from apps.client.permissions import IsAuthenticatedClient
from apps.client.serializers import ClientSerializer, LoginClientSerializer, RegisterClientSerializer, DepositVoucherClientSerializer, DepotClientSerializer, QueuePaymentVerificationClientSerializer
from config.helpers.authentications import MobilePhoneAuthenticationClient
from config.helpers.helper import extract_solde

from dotenv import load_dotenv
from django.utils import timezone

import os
import re
import requests
from datetime import datetime, timedelta
from decimal import Decimal

load_dotenv()


class ProfileClientView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []

    def get(self, request):
        serializer = ClientSerializer(request.client, context={'request': request})
        client = serializer.data
        if not client['is_active']:
            return Response({'error': 'Accès refusé: votre compte doit être actif. Veuillez vous connecter pour continuer.'}, status=403)
        return Response(client, status=200)

class LogoutClientView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []

    def put(self, request:Request):
        try:
            client = Client.objects.get(id=request.client.id)
            client.is_active = False
            client.save()
            return Response({'message':'Utilisateur déconnecté avec succès.'}, status=200)
        except Client.DoesNotExist:
            return Response({'erreur':"Client non existant"}, status=404)

class LoginClientView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginClientSerializer

    def post(self, request):
        # request.data.keys = ['email', 'password']
        serializer = LoginClientSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterClientView(APIView):
    permission_classes = [AllowAny]
    
    def check_if_client_exist(self, email):
        return Client.objects.filter(email=email).exists() or User.objects.filter(email=email).exists()
        
    def post(self, request):
        # request.data.keys = ['first_name', 'last_name','email','password','contact', 'sexe', 'adress']
        try:
            if self.check_if_client_exist(request.data['email']):
                return Response({'erreur':'email existant'},status=400)
            user_data = request.data
            if user_data.get('sexe', 'I').lower() not in ['masculin', 'feminin']: user_data['sexe'] = 'I'
            else: user_data['sexe'] = user_data['sexe'].strip()[0].upper()
            serializer = RegisterClientSerializer(data=user_data)
            if serializer.is_valid(raise_exception=True):
                return Response({'email':serializer.validated_data['email']}, status=status.HTTP_201_CREATED)
            else:
                return Response({'erreur':'erreur de serialisation'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
################################################################################
#                                                                              #
#                         CLIENT DEPOT/TRANSACTION                             #
#                                                                              #
################################################################################

class ClientDepotView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []

    def get(self, request):
        client = request.client
        depots = client.depots.order_by('-created_at')
        queues = client.queues.order_by('-created_at')
        data = {
            "depots": DepotClientSerializer(depots, many=True).data,
            "queues": QueuePaymentVerificationClientSerializer(queues, many=True).data
        }
        
        return Response(data, status=status.HTTP_200_OK)

class ClientDepotVerification(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = [MobilePhoneAuthenticationClient]
    
    def validate_and_convert_date(self,date_string):
        formats = {
            'jj-mm-aaaa': r'^\d{2}-\d{2}-\d{4}$',
            'jj/mm/aaaa': r'^\d{2}/\d{2}/\d{4}$',
            'aaaa-mm-jj': r'^\d{4}-\d{2}-\d{2}$',
            'aaaa/mm/jj': r'^\d{4}/\d{2}/\d{2}$',
        }

        if re.match(formats['jj-mm-aaaa'], date_string):
            return datetime.strptime(date_string, '%d-%m-%Y').date()
        elif re.match(formats['jj/mm/aaaa'], date_string):
            return datetime.strptime(date_string, '%d/%m/%Y').date()
        elif re.match(formats['aaaa-mm-jj'], date_string):
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        elif re.match(formats['aaaa/mm/jj'], date_string):
            return datetime.strptime(date_string, '%Y/%m/%d').date()
        else:
            raise ValueError(f"Le format de la date '{date_string}' est invalide.")

    def validate_data(self, data):
        attrs = ["mode_payement", "reference","numero_source","date_payement"]
        attributs_complete = all(attr in attrs for attr in data.keys()) and \
            len(data.keys()) == 4  and all(attr in data.keys()for attr in attrs)
        if not attributs_complete:
            return False
        mode_payement = data["mode_payement"]
        if mode_payement.strip().lower() not in ["mvola","orangemoney","airtelmoney"]:
            return False
        return self.validate_mode_payement_and_numero_source(mode_payement, data["numero_source"])
            
    def validate_mode_payement_and_numero_source(self, mode_payement, numero):
        mode_payement, numero = mode_payement.lower().strip(), str(numero).replace(" ","")
        try:
            pays_numero_start_code = os.getenv("PAYS_NUMERO_START_CODE")
            PAYMENT_START_NUMERO = {
                "mvola":["034", "038", pays_numero_start_code+"34", pays_numero_start_code+"38"],
                "orangemoney":["032", "037", pays_numero_start_code+"32",pays_numero_start_code+"37"],
                # "airtelmoney":["033", pays_numero_start_code+"33"]
                }
            valid_numero = any(numero.startswith(start_num)for start_num in PAYMENT_START_NUMERO[mode_payement])
            return valid_numero
        except Exception as e:
            return False
            
    def message_is_already_used(self, data):
        return DepotClient.objects.filter(reference=data["reference"], mode_payement=data["mode_payement"].strip().upper()[0], numero_source=data["numero_source"]).exists() 

    def post(self, request):
        try:
            # request.data = ['mode_payement', 'reference', 'numero_source', 'date_payement']
            if not self.validate_data(request.data):
                return Response({"erreur":"Tous les attributs sont requis, veuillez reverifier"}, status=status.HTTP_400_BAD_REQUEST)
            if self.message_is_already_used(request.data):
                return Response({"erreur":"Message dejà utilisé auparavant!"}, status=status.HTTP_401_UNAUTHORIZED)
            mode_payement = request.data['mode_payement']
            reference = request.data['reference']
            numero_source = request.data['numero_source']
            date_valid = self.validate_and_convert_date(request.data['date_payement'])
            date_payement = date_valid.strftime("%d-%m-%Y")

            token_access = TokenPairMobileAuthentication.objects.last().token_access
            request_url = os.getenv("MOBILE_REQUEST_URL") + "/api/ikom/mobilemoney/filter"

            data = {
                "mode_payment": mode_payement,
                "reference": reference,
                "numero": numero_source,
                "date": date_payement
            }
            headers = {"Authorization": f"Bearer {token_access}", "Content-Type":"Application/json"}
            response = requests.post(request_url, json=data, headers=headers)
            print(response)
            if response.status_code == status.HTTP_200_OK:
                try:
                    result = response.json()
                    solde, currency = extract_solde(result['body'])
                    solde_decimal = Decimal(solde.replace(" ", ""))

                    DepotClient.objects.create(
                        client=request.client,
                        numero_source=numero_source,
                        reference=reference,
                        date_payement=date_valid.strftime("%Y-%m-%d"),
                        mode_payement=mode_payement.upper()[0],
                        solde=solde_decimal,
                        currency=currency,
                        status='S'
                    )

                    deposit_client, created = DepositVoucherClient.objects.get_or_create(
                        client=request.client
                    )
                    deposit_client.amount = deposit_client.amount + solde_decimal
                    deposit_client.modified_at = timezone.now() + timedelta(hours=3)
                    deposit_client.save()

                    return Response({
                        'message': 'Paiement validé avec succès',
                        'solde': str(solde).strip() + str(currency).strip()
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif 400 <= response.status_code < 500:
                QueuePaymentVerificationClient.objects.update_or_create(
                        client=request.client,
                        mode_payement=mode_payement.upper()[0],
                        reference=reference,
                        defaults={
                            'numero_source': numero_source,
                            'date_payement': date_valid.strftime("%Y-%m-%d"),
                            'status': 'F'
                        }
                    )
                return Response({'message': 'Faillure de verification de dépot, veuillez verifie vos informations et réessayer plutard.'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'erreur': 'Erreur de paiement, veuillez réessayer.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({'erreur': 'Erreur interne lors du traitement du paiement.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentVerificationStatusClientView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []
    
    def get(self, request, reference):
        try:
            queue_payment = QueuePaymentVerificationClient.objects.get(reference=reference, client=request.client)
            
            position = QueuePaymentVerificationClient.objects.filter(status='P', created_at__lt=queue_payment.created_at).count() + 1
            total_pending = QueuePaymentVerificationClient.objects.filter(status='P').count()
            
            if total_pending > 0:
                progress_percentage = (position / total_pending) * 100
            else:
                progress_percentage = 100
            
            return Response({
                'status': queue_payment.get_status_display(),
                'progress_percentage': progress_percentage,
                'position_in_queue': position,
                'total_pending': total_pending
            }, status=status.HTTP_200_OK)
        
        except QueuePaymentVerificationClient.DoesNotExist:
            return Response({'error': 'Vérification de paiement introuvable.'}, status=status.HTTP_404_NOT_FOUND)

class ClientDepositVoucherClientView(APIView):
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = []

    def get(self, request):
        client = request.client
        deposit_vouchers = DepositVoucherClient.objects.filter(client=client)
        if not deposit_vouchers.exists():
            return Response([], status=status.HTTP_200_OK)
        deposit_voucher_serializer = DepositVoucherClientSerializer(deposit_vouchers.first())
        return Response(deposit_voucher_serializer.data, status=status.HTTP_200_OK)
