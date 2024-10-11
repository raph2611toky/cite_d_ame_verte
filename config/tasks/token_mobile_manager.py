from apps.client.models import TokenPairMobileAuthentication

from config.helpers.helper import get_timezone

from dotenv import load_dotenv
import os
import requests

load_dotenv()

def login_all_nigth():
    try:
        mobile_username = os.getenv("MOBILE_COMPTE_USERNAME")
        mobile_password = os.getenv("MOBILE_COMPTE_PASSWORD")
        request_url = os.getenv("MOBILE_REQUEST_URL") + "/users/login"

        data = {
            'username': mobile_username,
            'password': mobile_password
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(request_url, json=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()

            token_access = tokens['accessToken']
            token_refresh = tokens['refreshToken']
            
            token_pair = TokenPairMobileAuthentication.objects.all()
            if token_pair.count() != 0:
                token_pair.last().delete()
            
            now = get_timezone()
            TokenPairMobileAuthentication.objects.create(token_access=token_access,token_refresh=token_refresh,modify_at=now)
            print("Tokens successfully updated.")
        else:
            print("Login failed: ", response.status_code, response.text)

    except Exception as e:
        print(f"An error occurred during login: {e}")
        

def refresh_token_all_ten_minutes(force_token=True):
    try:
        request_url = os.getenv("MOBILE_REQUEST_URL") + "/token/refresh"

        token_obj = TokenPairMobileAuthentication.objects.last()
        if not token_obj:
            login_all_nigth()
        else:
            refresh_token = token_obj.token_refresh
            access_token = token_obj.token_access
            data = {
                'refreshToken':refresh_token
            }

            headers = {
                "Content-Type": "Application/json",
                'Authorization': f'Bearer {access_token}',
            }
            response = requests.post(request_url, json=data, headers=headers)
            if response.status_code == 200:
                print("refresh token is avalaible.....")
                tokens = response.json()

                token_access = tokens['accessToken']
                token_refresh = tokens['refreshToken']
                token_obj.token_access = token_access
                token_obj.token_refresh = token_refresh
                token_obj.modify_at = get_timezone()
                token_obj.save()

                print("Token access successfully refreshed.")
            else:
                print("Failed to refresh token: ", response.status_code, response.json())
                if force_token:
                    login_all_nigth()

    except Exception as e:
        print(f"An error occurred during token refresh: {e}")
        if force_token:
            login_all_nigth()