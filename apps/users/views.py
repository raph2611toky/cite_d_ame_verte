from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import TokenError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import User, AccountMode, UserSubscription, DepositVoucherUser, DepotUser, QueuePaymentVerificationUser
from apps.client.models import Client, TokenPairMobileAuthentication
from apps.users.serializers import UserSerializer, LoginSerializer, RegisterSerializer, AccountModeSerializer, UserSubscriptionSerializer, QueuePaymentVerificationUserSerializer, DepotUserSerializer, DepositVoucherUserSerializer
from config.helpers.authentications import MobilePhoneAuthenticationUser
from config.helpers.helper import extract_solde

from dotenv import load_dotenv
from django.utils import timezone

import os
import re
import requests
from datetime import datetime, timedelta
from decimal import Decimal


load_dotenv()


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        user = serializer.data
        if not user['is_active']:
            return Response({'error': 'Accès refusé: votre compte doit être actif. Veuillez vous connecter pour continuer.'}, status=403)
        return Response(user, status=200)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request:Request):
        try:
            user = User.objects.get(id=request.user.id)
            user.is_active = False
            user.save()
            return Response({'message':'Utilisateur déconnecté avec succès.'}, status=200)
        except User.DoesNotExist:
            return Response({'erreur':"Utilisateur non trouvé"}, status=404)

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        # request.data.keys = ['email', 'password']
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def check_if_user_exist(self, email):
        return User.objects.filter(email=email).exists() or Client.objects.filter(email=email).exists()
    
    def validate_data(self, data):
        try:
            keys = ['first_name','last_name','email', 'adress','password','contact', 'sexe', 'domaine', 'profession', 'organisation']
            if any(key not in data.keys() for key in keys):
                return False
            return True
        except Exception as e:
            return False
    
    
    def post(self, request):
        # request.data.keys = ['first_name','last_name','email','password','contact', 'sexe', 'adress', 'domaine', 'profession', 'organisation']
        try:
            if not self.validate_data(request.data):
                return Response({'erreur':'Tous les attributs sont requis'}, status=status.HTTP_400_BAD_REQUEST)
            if self.check_if_user_exist(request.data['email']):
                return Response({'erreur':'email existant'},status=400)
            user_data = request.data
            if user_data.get('sexe', 'I').lower() not in ['masculin', 'feminin']: user_data['sexe'] = 'I'
            else: user_data['sexe'] = user_data['sexe'].strip()[0].upper()
            serializer = RegisterSerializer(data=user_data)
            if serializer.is_valid(raise_exception=True):
                # serializer.save()
                return Response({"email":serializer.validated_data["email"]}, status=status.HTTP_201_CREATED)
            else:
                return Response({'erreur':'erreur de serialisation'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AccountModeListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            accounts_mode = AccountModeSerializer(AccountMode.objects.all(),many=True).data
            return Response(accounts_mode, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ConfigureAccountMode(APIView):
    permission_classes = [IsAuthenticated]
    
    def validate_data(self, data):
        try:
            return AccountMode.objects.filter(id_account_mode=data['account_mode']).exists()
        except Exception:
            return False
    
    def post(self, request):
        # request.data = ['account_mode']
        try:
            if not self.validate_data(request.data):
                return Response({'erreur': 'mode de compte invalid'}, status=status.HTTP_404_NOT_FOUND)
            account_mode = AccountMode.objects.get(id_account_mode=request.data['account_mode'])
            UserSubscription.objects.create(user=request.user, account_mode=account_mode)
            return Response({'message': 'Configuration reussi'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
################################################################################
#                                                                              #
#                         CLIENT DEPOT/TRANSACTION                             #
#                                                                              #
################################################################################

class UserDepotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        depots = user.depots.order_by('-created_at')
        queues = user.queues.order_by('-created_at')
        data = {
            "depots": DepotUserSerializer(depots, many=True).data,
            "queues": QueuePaymentVerificationUserSerializer(queues, many=True).data
        }
        
        return Response(data, status=status.HTTP_200_OK)

class UserDepotVerification(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [MobilePhoneAuthenticationUser]
    
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
        return DepotUser.objects.filter(reference=data["reference"], mode_payement=data["mode_payement"].strip().upper()[0], numero_source=data["numero_source"]).exists() 

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

                    DepotUser.objects.create(
                        user=request.user,
                        numero_source=numero_source,
                        reference=reference,
                        date_payement=date_valid.strftime("%Y-%m-%d"),
                        mode_payement=mode_payement.upper()[0],
                        solde=solde_decimal,
                        currency=currency,
                        status='S'
                    )

                    deposit_user, created = DepositVoucherUser.objects.get_or_create(
                        user=request.user
                    )
                    deposit_user.amount = deposit_user.amount + solde_decimal
                    deposit_user.modified_at = timezone.now() + timedelta(hours=3)
                    deposit_user.save()

                    return Response({
                        'message': 'Paiement validé avec succès',
                        'solde': str(solde).strip() + str(currency).strip()
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"erreur":str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif 400 <= response.status_code < 500:
                QueuePaymentVerificationUser.objects.update_or_create(
                        user=request.user,
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

class PaymentVerificationStatusUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, reference):
        try:
            queue_payment = QueuePaymentVerificationUser.objects.get(reference=reference, user=request.user)
            
            position = QueuePaymentVerificationUser.objects.filter(status='P', created_at__lt=queue_payment.created_at).count() + 1
            total_pending = QueuePaymentVerificationUser.objects.filter(status='P').count()
            
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
        
        except QueuePaymentVerificationUser.DoesNotExist:
            return Response({'error': 'Vérification de paiement introuvable.'}, status=status.HTTP_404_NOT_FOUND)

class UserDepositVoucherUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        deposit_vouchers = DepositVoucherUser.objects.filter(user=user)
        if not deposit_vouchers.exists():
            return Response([], status=status.HTTP_200_OK)
        deposit_voucher_serializer = DepositVoucherUserSerializer(deposit_vouchers.first())
        return Response(deposit_voucher_serializer.data, status=status.HTTP_200_OK)

