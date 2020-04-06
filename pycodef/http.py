import base64
import json
import os
import requests
from urllib.parse import quote, unquote_plus
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5


BASE_URL = os.environ.get('PYCODEF_BASE_URL')


def string_to_base64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64_to_string(b):
    return base64.b64decode(b).decode('utf-8')


def request_token():
    client_id = os.environ.get('PYCODEF_CLIENT_ID')
    client_secret = os.environ.get('PYCODEF_CLIENT_SECRET')
    url = os.environ.get('PYCODEF_REQUEST_TOKEN_URL', 'https://oauth.codef.io/oauth/token')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + string_to_base64(client_id + ':' + client_secret).decode('utf-8')
    }
    response = requests.post(url, data='grant_type=client_credentials&scope=read', headers=headers)
    return response


def http_sender(url, body):
    def _sender(token):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        return requests.post(url, data=quote(str(json.dumps(body))), headers=headers)

    access_token = ''
    try:
        response = _sender(access_token)
        assert response.status_code == 200
    except AssertionError:
        request_token_response = request_token()
        assert request_token_response.status_code == 200
        access_token = json.loads(request_token_response.text)['access_token']
        response = _sender(access_token)

    return response


def fetch_connected_id_list(page_no):
    response = http_sender(BASE_URL + '/v1/account/connectedId-list', body={'pageNo': page_no})
    assert response.status_code == 200
    response_body = json.loads(unquote_plus(response.text))
    return response_body


def fetch_account_list(connected_id):
    response = http_sender(BASE_URL + '/v1/account/list', body={'connectedId': connected_id})
    assert response.status_code == 200
    response_body = json.loads(unquote_plus(response.text))
    return response_body


def fetch_account_transaction_list(request_body):
    response = http_sender(BASE_URL + '/v1/kr/bank/p/account/transaction-list', body=request_body)
    assert response.status_code == 200
    response_body = json.loads(unquote_plus(response.text))
    return response_body
