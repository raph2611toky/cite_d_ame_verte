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