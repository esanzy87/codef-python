import unittest
from . import invoker_factory


class CommonTestCase(unittest.TestCase):
    """
    관리단에 해당하는 공통 API 테스트케이스
    """
    @classmethod
    def setUpClass(cls):
        cls.invoker = invoker_factory.get_invoker()
        cls.connected_id = '8OLsIxnamncje8lkUuKax-O'

    def test_fetch_connected_id_list(self):
        """
        전체 커넥티드 아이디 목록 조회

        :return:
        """
        response_body = self.invoker.fetch_connected_id_list()
        self.assertEqual(response_body['result']['code'], 'CF-00000')

    def test_fetch_organization_list(self):
        """
        커넥티드 아이디에 연동된 금융기관 (은행/카드) 리스트 조회

        :return:
        """
        response_body = self.invoker.fetch_account_list(connected_id=self.connected_id)
        self.assertEqual(response_body['result']['code'], 'CF-00000')


if __name__ == '__main__':
    unittest.main()
