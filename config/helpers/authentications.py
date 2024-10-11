from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from django.contrib.auth import get_user_model

from apps.client.models import DepotClient, QueuePaymentVerificationClient
from apps.client.permissions import IsAuthenticatedClient
from apps.users.models import DepotUser, QueuePaymentVerificationUser

from config.helpers.helper import get_token_from_request, get_client, get_user
from django.contrib.auth.models import AnonymousUser

from datetime import datetime

import re
import os
import socket

User = get_user_model()


class MobileIsUnreachable(APIException):
    status_code = 503
    default_detail = 'Le téléphone mobile pour la vérification de paiement est injoignable. Veuillez réessayer plus tard.'
    default_code = 'service_indisponible'

def is_reachable(ip_address, port=80, timeout=4):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip_address, port))
        return True
    except (socket.error, Exception):
        return False

class UserOrClientAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        token = get_token_from_request(request)
        if token:
            client = get_client(token)
            if client is None or isinstance(client, AnonymousUser):
                request.client = AnonymousUser()
            elif not client.is_active:
                request.client = AnonymousUser()
            else:
                request.client = client
                return (None, token)
            user = get_user(token)
            if user is None or isinstance(user, AnonymousUser):
                request.user = AnonymousUser()
            elif not user.is_active:
                request.user = AnonymousUser()
            else:
                request.user = user
                return (user, token)
        return None
    
def validate_and_convert_date(date_string):
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
    
class MobilePhoneAuthenticationClient(BaseAuthentication):
            
    def validate_data(self, data):
        attrs = ["mode_payement", "reference","numero_source","date_payement"]
        attributs_complete = all(attr in attrs for attr in data.keys()) and \
            len(data.keys()) == 4  and all(attr in data.keys()for attr in attrs)
        if not attributs_complete:
            return False
        mode_payement = data["mode_payement"]
        if mode_payement.strip().lower() not in ["mvola","orangemoney","airtelmoney"]:
            return False
        return self.validate_mode_payement_and_numero_source(mode_payement, data["numero_source"]) and not self.message_is_already_used(data)
            
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
            print(e)
            return False
            
    def message_is_already_used(self, data):
        return DepotClient.objects.filter(reference=data["reference"], mode_payement=data["mode_payement"].strip().upper()[0], numero_source=data["numero_source"]).exists() 

    def make_request_in_queue(self, request):
        try:
            if not self.validate_data(request.data):
                raise MobileIsUnreachable
            date_valid = validate_and_convert_date(request.data['date_payement'])
            date_payement = date_valid.strftime("%Y-%m-%d")
            mode_payement = request.data["mode_payement"]
            QueuePaymentVerificationClient.objects.create(
                    client=request.client,
                    mode_payement=mode_payement.upper()[0],
                    reference=request.data["reference"],
                    numero_source=request.data["numero_source"],
                    date_payement=date_payement,
                    status='P'
                )
            print("request added in queue successfully...")
        except Exception:
            raise MobileIsUnreachable
    
    def verify_phonemobile_connectivity(self, request):
        try:
            phonemobile_ip_public = os.getenv("MOBILE_IP_PUBLIC")
            phonemobile_port = int(os.getenv("MOBILE_PORT"))
            phone_is_reachable = is_reachable(phonemobile_ip_public,port=phonemobile_port)
            if not phone_is_reachable:
                permission = IsAuthenticatedClient()
                if not permission.has_permission(request, None):
                    raise MobileIsUnreachable
                self.make_request_in_queue(request)
                raise MobileIsUnreachable
        except Exception:
            raise MobileIsUnreachable
        
    def authenticate(self, request):
        self.verify_phonemobile_connectivity(request)
        return None
    
class MobilePhoneAuthenticationUser(BaseAuthentication):
            
    def validate_data(self, data):
        attrs = ["mode_payement", "reference","numero_source","date_payement"]
        attributs_complete = all(attr in attrs for attr in data.keys()) and \
            len(data.keys()) == 4  and all(attr in data.keys()for attr in attrs)
        if not attributs_complete:
            return False
        mode_payement = data["mode_payement"]
        if mode_payement.strip().lower() not in ["mvola","orangemoney","airtelmoney"]:
            return False
        return self.validate_mode_payement_and_numero_source(mode_payement, data["numero_source"]) and not self.message_is_already_used(data)
            
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
            print(e)
            return False
            
    def message_is_already_used(self, data):
        return DepotUser.objects.filter(reference=data["reference"], mode_payement=data["mode_payement"].strip().upper()[0], numero_source=data["numero_source"]).exists() 

    def make_request_in_queue(self, request):
        try:
            if not self.validate_data(request.data):
                raise MobileIsUnreachable
            date_valid = validate_and_convert_date(request.data['date_payement'])
            date_payement = date_valid.strftime("%Y-%m-%d")
            mode_payement = request.data["mode_payement"]
            QueuePaymentVerificationUser.objects.create(
                    client=request.client,
                    mode_payement=mode_payement.upper()[0],
                    reference=request.data["reference"],
                    numero_source=request.data["numero_source"],
                    date_payement=date_payement,
                    status='P'
                )
            print("request added in queue successfully...")
        except Exception:
            raise MobileIsUnreachable
    
    def verify_phonemobile_connectivity(self, request):
        try:
            phonemobile_ip_public = os.getenv("MOBILE_IP_PUBLIC")
            phonemobile_port = int(os.getenv("MOBILE_PORT"))
            phone_is_reachable = is_reachable(phonemobile_ip_public,port=phonemobile_port)
            if not phone_is_reachable:
                permission = IsAuthenticated()
                if not permission.has_permission(request, None):
                    raise MobileIsUnreachable
                self.make_request_in_queue(request)
                raise MobileIsUnreachable
        except Exception:
            raise MobileIsUnreachable
        
    def authenticate(self, request):
        self.verify_phonemobile_connectivity(request)
        return None