"""
CODEF API를 이용하기 위한 Python binding


"""
import os
import unittest
from ..http import RequestFactory


# Environment Variables
CLIENT_ID = os.environ.get('CODEF_CLIENT_ID', 'ef27cfaa-10c1-4470-adac-60ba476273f9')
CLIENT_SECRET = os.environ.get('CODEF_CLIENT_SECRET', '83160c33-9045-4915-86d8-809473cdf5c3')
BASE_URL = os.environ.get('CODEF_BASE_URL', 'https://sandbox.codef.io')
PUBLIC_KEY = os.environ.get('CODEF_PUBLIC_KEY', '')
BANKING_USERID = os.environ.get('CODEF_PFX_FILE', '')
BANKING_PASSWORD = os.environ.get('CODEF_PFX_PASSWORD', '')


class HttpTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_factory = RequestFactory(CLIENT_ID, CLIENT_SECRET, BASE_URL, PUBLIC_KEY)
        cls.connected_id = '8OLsIxnamncje8lkUuKax-O'

    def test_request_token(self):
        response = self.request_factory.request_token()
        self.assertEqual(response.status_code, 200)

    def test_register_connected_id(self):
        business_type = 'BK'
        client_type = 'P'
        organization = '0003'
        response_body = self.request_factory.register_connected_id(
            organization,
            business_type=business_type,
            client_type=client_type,
            userid=BANKING_USERID,
            password=BANKING_PASSWORD
        )
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

    def test_fetch_creditcard_list(self):
        self.request_factory.add_account_to_connected_id(
            self.connected_id,
            business_type='CD',
            client_type='P',
            organization='0306',
            userid='12345',
            password='12345',
        )
        response_body = self.request_factory.fetch_creditcard_list(
            self.connected_id,
            '0306',
            '19901010',
        )
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_creditcard_approval_list(self):
        self.request_factory.add_account_to_connected_id(
            self.connected_id,
            '0306',
            business_type='CD',
            client_type='P',
            userid='12345',
            password='12345',
        )
        response_body = self.request_factory.fetch_creditcard_approval_list(
            self.connected_id,
            '0306',
            '19901010',
            '20200101',
            '20200131',
            '1111111111',
            '아무카드'
        )
        self.assertEqual(response_body['result']['code'], 'CF-00000')


if __name__ == '__main__':
    unittest.main()
