import unittest
from . import invoker_factory


class PersonalBankTestCase(unittest.TestCase):
    """
    은행기관 개인 금융 연동 테스트
    """
    @classmethod
    def setUpClass(cls):
        cls.invoker = invoker_factory.get_invoker('BK', 'P', '1')
        cls.connected_id = '8OLsIxnamncje8lkUuKax-O'
        cls.banking_userid = '12345'
        cls.banking_password = '12345'

    # 은행 계좌 연동 테스트
    def test_create_connected_id(self):
        """
        은행기관 연동으로 커넥티드 아이디 생성

        :return:
        """
        response_body = self.invoker.add_account(organization='0003', password=self.banking_password,
                                                 userid=self.banking_userid)
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_add_bank_organization_to_connected_id(self):
        """
        커넥티드 아이디에 은행기관 연동 추가

        :return:
        """
        response_body = self.invoker.add_account(organization='0088', password=self.banking_password,
                                                 userid=self.banking_userid, connected_id=self.connected_id)
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_account_list(self):
        """
        커넥티드 아이디에 연동된 은행기관의 보유 계좌 리스트 조회

        :return:
        """
        response_body = self.invoker.fetch_bank_account_list(connected_id=self.connected_id, organization='0088')
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_account_transaction_list(self):
        """
        은행 계좌의 입출금 내역 조회

        :return:
        """
        response_body = self.invoker.fetch_account_transaction_list(
            connected_id=self.connected_id,
            organization='0003',
            account='05308159900000',
            start_date='20190401',
            end_date='20190630',
        )
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_delete_account(self):
        response_body = self.invoker.delete_account(connected_id=self.connected_id, organization='0088')
        self.assertEqual(response_body['result']['code'], 'CF-00000')


if __name__ == '__main__':
    unittest.main()
