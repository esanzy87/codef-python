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


class InvokerFactory:
    def __init__(self, client_id, client_secret, base_url, public_key):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.public_key = public_key
        
    def get_invoker(self, business_type='BK', client_type='P', login_type='0', country_code='KR', access_token=''):
        """
        CODEF API를 호출하는 invoker 객체 생성 Factory method

        :param business_type: BK = 은행, CD = 카드
        :param client_type: P = 개인, B = 기업
        :param login_type: 0 = 공인인증서 방식, 1 = 아이디/패스워드 방식
        :param country_code: KR = 대한민국
        :param access_token: cookie, MQ 등에 미리 저장된 access_token
        :return:
        """
        assert business_type in ('BK', 'CD')  # BK = 은행, CD = 카드
        assert client_type in ('P', 'B')  # P = 개인, B = 기업
        assert login_type in ('0', '1')  # 0 = 공인인증서 방식, 1 = 아이디/패스워드 방식
        assert country_code == 'KR'  # KR = 대한민국
        return _Invoker(self.client_id, self.client_secret, self.base_url, self.public_key,
                        business_type, client_type, login_type, country_code, access_token)


class _Invoker:
    """
    CODEF API를 호출하는 invoker class
    """
    def __init__(self, client_id, client_secret, base_url, public_key, business_type, client_type, login_type,
                 country_code='KR', access_token=''):
        """
        
        :param client_id: 
        :param client_secret: 
        :param base_url: 
        :param public_key: 
        :param business_type: BK = 은행, CD = 카드 
        :param client_type: P = 개인, B = 기업
        :param login_type: 0 = 공인인증서 방식, 1 = 아이디/패스워드 방식
        :param country_code: KR = 대한민국
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.public_key = public_key
        self.business_type = business_type
        self.client_type = client_type
        self.login_type = login_type
        self.country_code = country_code
        self.access_token = access_token

    def __request_token(self):
        """
        access_token 요청

        :return:
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + string_to_base64(self.client_id + ':' + self.client_secret).decode('utf-8')
        }
        url = 'https://oauth.codef.io/oauth/token'
        data = 'grant_type=client_credentials&scope=read'
        response = requests.post(url, data=data, headers=headers)
        return response

    def http_sender(self, endpoint, body):
        """
        http API 호출 요청

        :param endpoint:
        :param body:
        :return:
        """
        url = self.base_url + endpoint
        data = quote(str(json.dumps(body)))

        try:
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.access_token}
            response = requests.post(url, data=data, headers=headers)
            assert response.status_code == 200
        except AssertionError:
            print("requesting new access token due to invalid token")
            request_token_response = self.__request_token()
            assert request_token_response.status_code == 200
            self.access_token = json.loads(request_token_response.text)['access_token']
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.access_token}
            response = requests.post(url, data=data, headers=headers)
        return response

    def add_account(self, organization, password, **kwargs):
        """
        기관 연동 추가

        connectedId가 매개변수로 넘어오는 경우 기존 connectedId에 기관 연동을 추가하고 넘어오지 않는 경우 새로운 connectedId를
        생성한다.

        :param organization: 4자리 기관코드
        :param password: 공인인증서 비밀번호 또는 인터넷뱅킹 비밀번호

        :return:
        """
        account_item = {
            'countryCode': self.country_code,
            'businessType': self.business_type,
            'clientType': self.client_type,
            'organization': organization,
            'loginType': self.login_type,
            'password': encrypt_rsa(self.public_key, password),
        }

        if self.login_type == '0':
            # 공인인증서 방식으로 인증하는 경우
            if 'pfx_file' in kwargs:
                account_item['certFile'] = kwargs['pfx_file']
                account_item['certType'] = 'pfx'
            else:
                account_item['derFile'] = kwargs['der_file']
                account_item['keyFile'] = kwargs['key_file']
        else:
            # 아이디 패스워드 방식으로 인증하는 경우
            account_item['id'] = kwargs['userid']

        if 'connected_id' not in kwargs:
            # 신규 connectedId 생성
            payload = {'accountList': [account_item]}
            endpoint = '/v1/account/create'
        else:
            # 기존 connectedId에 기관 연동 추가
            payload = {'accountList': [account_item], 'connectedId': kwargs['connected_id']}
            endpoint = '/v1/account/add'
        response = self.http_sender(endpoint=endpoint, body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        print(response_body)
        return response_body

    def add_accounts(self, organizations, connected_id=None):
        for org_info  in organizations:
            org_info['password'] = encrypt_rsa(self.public_key, org_info['password'])

        if not connected_id:
            # 신규 connectedId 생성
            payload = {'accountList': organizations}
            endpoint = '/v1/account/create'
        else:
            # 기존 connectedId에 기관 연동 추가
            payload = {'accountList': organizations, 'connectedId': connected_id}
            endpoint = '/v1/account/add'
        response = self.http_sender(endpoint=endpoint, body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def delete_account(self, connected_id,  organization):
        """
        기관 연동 삭제

        삭제 실행 후 connectedId에 남아있는 기관이 없는 경우 connectedId도 삭제

        :param connected_id: 기 등록된 커넥티드 아이디
        :param organization: 4자리 기관코드
        :return:
        """
        payload = {
            'connectedId': connected_id,
            'accountList': [
                {
                    'countryCode': self.country_code,
                    'businessType': self.business_type,
                    'clientType': self.client_type,
                    'organization': organization,
                    'loginType': self.login_type,
                }
            ]
        }
        response = self.http_sender('/v1/account/delete', body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_connected_id_list(self, page_no='0'):
        """
        커넥티드 아이디 목록 조회

        :param page_no:
        :return:
        """
        response = self.http_sender('/v1/account/connectedId-list', body={'pageNo': page_no})
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_account_list(self, connected_id):
        """
        커넥티드 아이디와 연동되어있는 기관 리스트 조회

        :param connected_id:
        :return:
        """
        response = self.http_sender('/v1/account/list', body={'connectedId': connected_id})
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_bank_account_list(self, connected_id, organization):
        """
        은행기관 보유계좌 조회

        :param connected_id:
        :param organization:
        :return:
        """
        payload = {
            "connectedId": connected_id,
            "organization": organization,
            "birthDate": "",
            "withdrawAccountNo": "",
            "withdrawAccountPassword": ""
        }

        if self.client_type == 'P':
            endpoint = '/v1/kr/bank/p/account/account-list'
        else:
            endpoint = '/v1/kr/bank/b/account/account-list'

        response = self.http_sender(endpoint, body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_account_transaction_list(self, connected_id, organization, account, start_date, end_date, order_by='0'):
        """
        입출금 내역 조회

        :param connected_id: 기 등록된 커넥티드 아이디
        :param organization: 4자리 기관코드
        :param account: 계좌번호
        :param start_date: 조회 시작일
        :param end_date: 조회 종료일
        :param order_by:
        :return:
        """
        payload = {
            'connectedId': connected_id,
            'organization': organization,
            'account': account,
            'startDate': start_date,
            'endDate': end_date,
            'orderBy': order_by,
            'inquiryType': '1'
        }

        if self.client_type == 'P':
            endpoint = '/v1/kr/bank/p/account/transaction-list'
        else:
            endpoint = '/v1/kr/bank/b/account/transaction-list'

        response = self.http_sender(endpoint, body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_creditcard_list(self, connected_id, organization, birthdate):
        """
        보듀 카드 조회

        :param connected_id:
        :param organization:
        :param birthdate:
        :return:
        """
        payload = {
            'connectedId': connected_id,
            'organization': organization,
            'birthDate': birthdate,
            'inquryType': '1'
        }

        if self.client_type == 'P':
            endpoint = '/v1/kr/card/p/account/card-list'
        else:
            endpoint = '/v1/kr/card/b/account/card-list'

        response = self.http_sender(endpoint, body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body

    def fetch_creditcard_approval_list(self, connected_id, organization, birthdate, start_date, end_date, card_no,
                                       card_name):
        payload = {
            'connectedId': connected_id,
            'organization': organization,
            'birthDate': birthdate,
            'startDate': start_date,
            'endDate': end_date,
            'orderBy': '0',
            'inquiryType': '0',
            'cardNo': card_no,
            'cardName': card_name,
            'duplicateCardIdx': '1',
            'memberStoreInfoType': '0',
        }

        if self.client_type == 'P':
            endpoint = '/v1/kr/card/p/account/approval-list'
        else:
            endpoint = '/v1/kr/card/b/account/approval-list'

        response = self.http_sender(endpoint, body=payload)
        assert response.status_code == 200
        response_body = json.loads(unquote_plus(response.text))
        return response_body
