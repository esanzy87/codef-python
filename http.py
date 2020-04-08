import base64
import json
import requests
from urllib.parse import quote, unquote_plus
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5


def string_to_base64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64_to_string(b):
    return base64.b64decode(b).decode('utf-8')


def encrypt_rsa(public_key, data):
    key_der = base64.b64decode(public_key)
    key_pub = RSA.importKey(key_der)
    cipher = Cipher_PKCS1_v1_5.new(key_pub)
    cipher_text = cipher.encrypt(data.encode())
    return base64.b64encode(cipher_text).decode("utf-8")


def file_to_base64(filepath):
    with open(filepath, 'rb') as file_stream:
        data = file_stream.read()
    return base64.b64encode(data).decode('utf-8')


class RequestFactory:
    def __init__(self, client_id, client_secret, base_url, public_key, access_token='', country_code='KR'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.public_key = public_key
        self.access_token = access_token
        self.country_code = country_code

    def request_token(self):
        """
        access_token 요청

        :return:
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + string_to_base64(self.client_id + ':' + self.client_secret).decode('utf-8')
        }
        response = requests.post('https://oauth.codef.io/oauth/token', data='grant_type=client_credentials&scope=read',
                                 headers=headers)
        return response

    def http_sender(self, endpoint, body):
        """
        http API 호출 요청

        :param endpoint:
        :param body:
        :return:
        """
        def _sender(token):
            """
            실질적으로 요청을 담당하는 헬퍼 함수

            :param token:
            :return:
            """
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
            return requests.post(self.base_url + endpoint, data=quote(str(json.dumps(body))), headers=headers)

        try:
            response = _sender(self.access_token)
            assert response.status_code == 200
        except AssertionError:
            print("requesting new access token due to invalid token")
            request_token_response = self.request_token()
            assert request_token_response.status_code == 200
            self.access_token = json.loads(request_token_response.text)['access_token']
            response = _sender(self.access_token)
        return response

    def register_connected_id(self, business_type, client_type, organization, userid, password):
        """
        기관 연동 추가 (커넥티드 아이디가 없는 경우)

        :param business_type: BK = 은행, CD = 카드
        :param client_type: P = 개인, B = 기업
        :param organization: 4자리 기관코드
        :param userid: 인터넷뱅킹 아이디
        :param password: 인터넷뱅킹 비밀번호
        :return:
        """
        assert client_type in ('P', 'B')  # 고객구분(P: 개인, B: 기업)
        payload = {
            'accountList': [
                {
                    'countryCode': self.country_code,
                    'businessType': business_type,
                    'clientType': client_type,
                    'organization': organization,
                    'loginType': '1',
                    'id': userid,
                    'password': encrypt_rsa(self.public_key, password),
                }
            ]
        }
        response = self.http_sender('/v1/account/create', body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def add_account_to_connected_id(self, connected_id, business_type, client_type, organization, userid, password):
        """
        기관 연동 추가 (커넥티드 아이디가 있는 경우)

        :param connected_id: 기 등록된 커넥티드 아이디
        :param business_type: BK = 은행, CD = 카드
        :param client_type: P = 개인, B = 기업
        :param organization: 4자리 기관코드
        :param userid: 인터넷뱅킹 아이디
        :param password: 인터넷뱅킹 비밀번호
        :return:
        """
        assert client_type in ('P', 'B')  # 고객구분(P: 개인, B: 기업)
        payload = {
            'connectedId': connected_id,
            'accountList': [
                {
                    'countryCode': self.country_code,
                    'businessType': business_type,
                    'clientType': client_type,
                    'organization': organization,
                    'loginType': '1',
                    'id': userid,
                    'password': encrypt_rsa(self.public_key, password),
                }
            ]
        }
        response = self.http_sender('/v1/account/add', body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def delete_account_from_connected_id(self, connected_id, business_type, client_type, organization):
        """
        기관 연동 삭제

        :param connected_id: 기 등록된 커넥티드 아이디
        :param business_type: BK = 은행, CD = 카드
        :param client_type: P = 개인, B = 기업
        :param organization: 4자리 기관코드
        :return:
        """
        assert client_type in ('P', 'B')  # 고객구분(P: 개인, B: 기업)
        payload = {
            'connectedId': connected_id,
            'accountList': [
                {
                    'countryCode': self.country_code,
                    'businessType': business_type,
                    'clientType': client_type,
                    'organization': organization,
                    'loginType': '1',
                }
            ]
        }
        response = self.http_sender('/v1/account/delete', body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_connected_id_list(self, page_no):
        """
        커넥티드 아이디 목록 조회

        :param page_no:
        :return:
        """
        payload = {
            'pageNo': page_no
        }
        response = self.http_sender('/v1/account/connectedId-list', body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_account_list(self, connected_id):
        payload = {
            'connectedId': connected_id
        }
        response = self.http_sender('/v1/account/list', body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_account_transaction_list(self, connected_id, organization, account, start_date, end_date, order_by='0',
                                       inquiry_type='1'):
        """
        입출금 내역 조회

        :param connected_id: 기 등록된 커넥티드 아이디
        :param organization: 4자리 기관코드
        :param account: 계좌번호
        :param start_date: 조회 시작일
        :param end_date: 조회 종료일
        :param order_by:
        :param inquiry_type:
        :return:
        """
        payload = {
            'connectedId': connected_id,
            'organization': organization,
            'account': account,
            'startDate': start_date,
            'endDate': end_date,
            'orderBy': order_by,
            'inquiryType': inquiry_type
        }
        response = self.http_sender('/v1/kr/bank/p/account/transaction-list', body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body
