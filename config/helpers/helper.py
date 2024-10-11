from django.utils import timezone as django_timezone
from django.conf import settings
from rest_framework_simplejwt.tokens import TokenError
from rest_framework.request import Request
from django.contrib.auth.models import AnonymousUser

from apps.client.models import ClientOutstandingToken, Client
from apps.users.models import User

from dotenv import load_dotenv

from datetime import timedelta
import os
import re
import jwt

load_dotenv()

def get_timezone():
    tz = os.getenv("TIMEZONE_HOURS")
    if '-' in tz:
        return django_timezone.now() - timedelta(hours=int(tz.strip()[1:]))
    return django_timezone.now()+timedelta(hours=int(tz))


def is_token_blacklisted(token):
    try:
        if len(token.split('.')) != 3:
            raise TokenError("Invalid token structure")
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        jti = decoded_token.get('jti')
        if not jti:
            raise Exception('jti not found')
        outstanding_token = ClientOutstandingToken.objects.filter(jti=jti).first()
        if outstanding_token and outstanding_token.blacklisted:
            return True

        return False
    except (jwt.DecodeError, TokenError) as e:
        print(e)
        return True
    
def get_user(token):
    try:
        jwt_decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        user_id = jwt_decoded.get('user_id')
        if not user_id:
            return AnonymousUser()
        adminzone = User.objects.get(id=user_id)
        return AnonymousUser() if not adminzone else adminzone
    except (jwt.DecodeError, jwt.ExpiredSignatureError, User.DoesNotExist):
        return AnonymousUser()

def get_client(token):
    try:
        jwt_decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        client_id = jwt_decoded.get('client_id')
        if not client_id:
            return AnonymousUser()
        client = Client.objects.get(id=client_id)
        return AnonymousUser() if not client else client
    except (jwt.DecodeError, jwt.ExpiredSignatureError, Client.DoesNotExist):
        return AnonymousUser()
    
def get_token_from_request(request: Request) -> str:
    authorization_header = request.headers.get('Authorization')
    if authorization_header and authorization_header.startswith('Bearer '):
        return authorization_header.split()[1]
    return None

def extract_solde(body):
    if '1/2' in body:
        body = body.replace('1/2','')
    solde_pattern = r'(?<!\d[\d/])(\d{1,3}(?:[ \d]{0,12})?)\s*Ar'
    solde_match = re.search(solde_pattern, body)

    if solde_match:
        solde_str = solde_match.group()
        print(solde_str)
        if 'ar' not in solde_str.lower():
            return None
        if ' Ar'in solde_str:
            parts = solde_str.split()

            solde = ''.join(parts[:-1])
            currency = parts[-1]
        else:
            solde = solde_str.replace("Ar", "")
            currency = solde_str[-2:]
        return solde, currency
    else:
        return None