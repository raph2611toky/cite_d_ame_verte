from rest_framework import status
from config.helpers.helper import  extract_solde, get_timezone
from config.helpers.authentications import is_reachable

from apps.client.tasks.token_mobile_manager import login_all_nigth, refresh_token_all_ten_minutes
from apps.client.models import QueuePaymentVerificationClient, TokenPairMobileAuthentication, DepositVoucherClient, DepotClient

from dotenv import load_dotenv
from decimal import Decimal
import requests
import os

load_dotenv()

def process_payment_queue():
    try:
        print("process queue for client ....")
        phone_mobile_ip_public = os.getenv("MOBILE_IP_PUBLIC")
        phone_mobile_port = int(os.getenv("MOBILE_PORT"))
        phone_is_reachable = is_reachable(phone_mobile_ip_public, port=phone_mobile_port, timeout=4)
        print(f"phone reachable : {phone_is_reachable}")
        if not phone_is_reachable:
            return

        pending_payments = QueuePaymentVerificationClient.objects.filter(status='P')
        if pending_payments.count() > 0 :
            print("queues have pending request......")
            token_access = TokenPairMobileAuthentication.objects.last().token_access
            request_url = os.getenv("MOBILE_REQUEST_URL") + "/api/ikom/mobilemoney/filter"
            if TokenPairMobileAuthentication.objects.all().count() == 0:
                login_all_nigth()
            else:
                refresh_token_all_ten_minutes()
            token_access = TokenPairMobileAuthentication.objects.last().token_access
            for queue_payment in pending_payments:
                try:
                    MODE_PAYEMENT = {"M":"mvola", "O":"orangemoney", "A":"airtelmoney"}
                    data = {
                        "mode_payment": MODE_PAYEMENT[queue_payment.mode_payement],
                        "reference": queue_payment.reference,
                        "numero": queue_payment.numero_source,
                        "date": queue_payment.date_payement.strftime("%d-%m-%Y")
                    }
                    headers = {"Authorization": f"Bearer {token_access}", "Content-Type":"Application/json"}

                    response = requests.post(request_url, json=data, headers=headers)
                    print(request_url,data, headers)
                    print(response)
                    print(response.text)
                    if response.status_code == status.HTTP_200_OK:
                        result = response.json()
                        solde, currency = extract_solde(result['body'])
                        solde_decimal = Decimal(solde.replace(" ", ""))
                        DepotClient.objects.create(
                            client=queue_payment.client,
                            numero_source=queue_payment.numero_source,
                            reference=queue_payment.reference,
                            date_payement=queue_payment.date_payement,
                            mode_payement=queue_payment.mode_payement,
                            solde=solde_decimal,
                            currency=currency,
                            status='S'
                        )
                        print("depot success ...")

                        deposit_client, created = DepositVoucherClient.objects.get_or_create(
                            client=queue_payment.client
                        )
                        deposit_client.amount = deposit_client.amount + solde_decimal
                        deposit_client.modified_at = get_timezone()
                        deposit_client.save()
                        print("deposit client  success....")

                        queue_payment.status = 'S'
                        queue_payment.save()

                    elif response.status_code == status.HTTP_400_BAD_REQUEST:
                        queue_payment.status = 'F'
                        queue_payment.save()

                except requests.exceptions.RequestException as e:
                    print(f"Erreur lors de la communication avec l'API: {e}")
                    continue
    except Exception as e:
        print(e)