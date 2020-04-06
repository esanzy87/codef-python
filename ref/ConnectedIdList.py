# -*- coding: utf-8 -*-
# UTF-8 encoding when using korean
#######################################
##      ConnectedId 목록조회
######################################
import requests, json, base64
import urllib

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5

# ========== HTTP 기본 함수 ==========

def http_sender(url, token, body):
    headers = {'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

    response = requests.post(url, headers = headers, data = urllib.parse.quote(str(json.dumps(body))))

    print('response.status_code = ' + str(response.status_code))
    print('response.text = ' + urllib.parse.unquote_plus(response.text))

    return response
# ========== HTTP 함수  ==========

# ========== Toekn 재발급  ==========
def request_token(url, client_id, client_secret):
    authHeader = stringToBase64(client_id + ':' + client_secret).decode("utf-8")

    headers = {
        'Acceppt': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + authHeader
        }

    response = requests.post(url, headers = headers, data = 'grant_type=client_credentials&scope=read')

    print(response.status_code)
    print(response.text)

    return response
# ========== Toekn 재발급  ==========

# ========== Encode string data  ==========
def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')
# ========== Encode string data  ==========

# token URL
token_url = 'https://oauth.codef.io/oauth/token'

# 기 발급된 토큰
token =''
##############################################################################
##                               ConnectedId 목록조회                         ##
##############################################################################
# Input Param
#
# pageNo : 페이지 번호(생략 가능) 생략시 1페이지 값(0) 자동 설정
#
##############################################################################
codef_connected_id_list_url = 'https://development.codef.io/v1/account/connectedId-list'
codef_connected_id_list_body = {
    'pageNo':'5'            # 페이지 번호(생략 가능) 생략시 1페이지 값(0) 자동 설정
}

response_connected_id_list = http_sender(codef_connected_id_list_url, token, codef_connected_id_list_body)
if response_connected_id_list.status_code == 200:      # success
    dict = json.loads(urllib.unquote_plus(response_connected_id_list.text.encode('utf8')))
    if 'data' in dict and str(dict['data']) != '{}':
        print('조회 정상 처리')
    else:
        print('조회 오류')
elif response_connected_id_list.status_code == 401:      # token error
    dict = json.loads(response_connected_id_list.text)
    # invalid_token
    print('error = ' + dict['error'])
    # Cannot convert access token to JSON
    print('error_description = ' + dict['error_description'])

    # reissue token
    response_oauth = request_token(token_url, 'CODEF로부터 발급받은 클라이언트 아이디', 'CODEF로부터 발급받은 시크릿 키')
    if response_oauth.status_code == 200:
        dict = json.loads(response_oauth.text)
        # reissue_token
        token = dict['access_token']
        print('access_token = ' + token)

        # request codef_api
        response = http_sender(codef_account_create_url, token, codef_account_create_body)
        if response.status_code == 200:      # success
            dict = json.loads(urllib.parse.unquote_plus(response.text))
            if 'data' in dict and str(dict['data']) != '{}':
                print('조회 정상 처리')
            else:
                print('조회 오류')
    else:
        print('토큰발급 오류')
else:
    print('조회 오류')
