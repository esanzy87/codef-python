"""
CODEF API를 이용하기 위한 Python binding


"""
import os
import unittest
from pycodef.http import RequestFactory


# Environment Variables
REQUEST_TOKEN_URL = os.environ.get('PYCODEF_REQUEST_TOKEN_URL', 'https://oauth.codef.io/oauth/token')
CLIENT_ID = os.environ.get('PYCODEF_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('PYCODEF_CLIENT_SECRET', '')
BASE_URL = os.environ.get('PYCODEF_BASE_URL', 'https://development.codef.io')
PUBLIC_KEY = os.environ.get('PYCODEF_PUBLIC_KEY', '')
PFX_FILE = os.environ.get('PYCODEF_PFX_FILE', '')
PFX_PASSWORD = os.environ.get('PYCODEF_PFX_PASSWORD', '')


class HttpTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_factory = RequestFactory(REQUEST_TOKEN_URL, CLIENT_ID, CLIENT_SECRET, BASE_URL, PUBLIC_KEY)
        cls.connected_id = '8OLsIxnamncje8lkUuKax-O'

    def test_request_token(self):
        response = self.request_factory.request_token()
        self.assertEqual(response.status_code, 200)

    def test_register_connected_id(self):
        country_code = 'KR'
        business_type = 'BK'
        client_type = 'P'
        organization = '0003'
        login_type = '0'
        response_body = self.request_factory.register_connected_id(country_code, business_type, client_type, organization, login_type, PFX_PASSWORD, PFX_FILE)
        print(response_body['data'])
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_connected_id_list(self):
        response_body = self.request_factory.fetch_connected_id_list(page_no='5')
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_account_list(self):
        response_body = self.request_factory.fetch_account_list(self.connected_id)
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_account_transaction_list(self):
        response_body = self.request_factory.fetch_account_transaction_list(
            self.connected_id,
            '0003',
            '05308159900000',
            '20190401',
            '20190630',
        )
        self.assertEqual(response_body['result']['code'], 'CF-00000')


if __name__ == '__main__':
    unittest.main()
