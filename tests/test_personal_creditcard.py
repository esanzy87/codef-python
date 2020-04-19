import unittest
from . import invoker_factory


class PersonalCreditCardTestCase(unittest.TestCase):
    """
    신용카드 개인 금융 연동 테스트
    """
    @classmethod
    def setUpClass(cls):
        cls.invoker = invoker_factory.get_invoker('CD', 'P', '1')
        cls.connected_id = '8OLsIxnamncje8lkUuKax-O'
        cls.banking_userid = '12345'
        cls.banking_password = '12345'

    # 신용카드 연동 테스트
    def test_create_connected_id(self):
        """
        신용카드 연동으로 커넥티드 아이디 생성

        :return:
        """
        response_body = self.invoker.add_account(organization='0301', password=self.banking_password,
                                                 userid=self.banking_userid)
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_add_creditcard_organization(self):
        """
        커넥티드아이디에 신용카드 기관 연동 추가

        :return:
        """
        response_body = self.invoker.add_account(organization='0301', password=self.banking_password,
                                                 userid=self.banking_userid, connected_id=self.connected_id)
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_creditcard_list(self):
        response_body=self.invoker.fetch_creditcard_list(
            connected_id=self.connected_id,
            organization='0301',
            birthdate='19901010',
        )
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_creditcard_approval_list(self):
        response_body = self.invoker.fetch_creditcard_approval_list(
            connected_id=self.connected_id,
            organization='0301',
            birthdate='19901010',
            start_date='20200101',
            end_date='20200131',
            card_no='1111111111',
            card_name='아무카드',
        )
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_delete_account(self):
        response_body = self.invoker.delete_account(connected_id=self.connected_id, organization='0301')
        self.assertEqual(response_body['result']['code'], 'CF-00000')


if __name__ == '__main__':
    unittest.main()
