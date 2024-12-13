import base64
import requests
from datetime import datetime
from django.conf import settings

def mpesa_stk_push(phone_number, amount):
    lipa_na_mpesa_online_shortcode = settings.MPESA_SHORTCODE
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_string = lipa_na_mpesa_online_shortcode + passkey + timestamp
    password_base64 = base64.b64encode(password_string.encode('utf-8')).decode('utf-8')

    # API URLs for Safaricom M-Pesa
    lipa_na_mpesa_online_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # Sandbox URL for testing

    headers = {
        "Authorization": f"Bearer {generate_access_token()}"
    }

    payload = {
        "BusinessShortCode": lipa_na_mpesa_online_shortcode,
        "Password": password_base64,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": lipa_na_mpesa_online_shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://mydomain.com/path",
        "AccountReference": "DigiHarvest",
        "TransactionDesc": "Purchase of goods"
    }

    response = requests.post(lipa_na_mpesa_online_url, json=payload, headers=headers)
    print(response.status_code)
    print(response.text)
    return response.json()

def generate_access_token():
    # Generate access token to authenticate with M-Pesa API
    credentials = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    response = requests.get(auth_url, headers=headers)
    print(response.json()["access_token"])
    return response.json()['access_token']
