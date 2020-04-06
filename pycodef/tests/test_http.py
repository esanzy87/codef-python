"""
CODEF API를 이용하기 위한 Python binding

Agenda
* 각 API를 호출할 때 access_token을 넘겨주는 부분을 빼고 자동으로 access_token의 유효성을 체크하여 필요 시 요청하도록 하는 부분 추가하기


"""
import unittest
from pycodef.http import request_token, fetch_connected_id_list, fetch_account_list, fetch_account_transaction_list


class RequestTokenTestCase(unittest.TestCase):
    def test_request_token(self):
        response = request_token()
        self.assertEqual(response.status_code, 200)


class HandleConnectedIdTestCase(unittest.TestCase):
    def test_fetch_connected_id_list(self):
        response_body = fetch_connected_id_list(page_no='5')
        self.assertEqual(response_body['result']['code'], 'CF-00000')


class HandleBankAccountTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connected_id = '8OLsIxnamncje8lkUuKax-O'

    def test_fetch_account_list(self):
        response_body = fetch_account_list(self.connected_id)
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_account_transaction_list(self):
        request_body = {
            'connectedId': 'sandbox_connectedId',
            'organization': '0003',
            'account': '05308159900000',
            'startDate': '20190401',
            'endDate': '20190630',
            'orderBy': '0',
            'inquiryType': '1'
        }
        response_body = fetch_account_transaction_list(request_body)
        self.assertEqual(response_body['result']['code'], 'CF-00000')


if __name__ == '__main__':
    unittest.main()
