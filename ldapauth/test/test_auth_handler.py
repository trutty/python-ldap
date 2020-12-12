import unittest
from ldapauth.main.auth_handler import AuthHandler
from ldap3 import Server, Connection, MOCK_SYNC


class MockConnectionProvider:

    @staticmethod
    def connection(user_dn, password):
        conn = Connection(
            Server('my-fake-server'),
            user_dn, password,
            raise_exceptions=False, lazy=False, client_strategy=MOCK_SYNC
        )
        conn.strategy.add_entry(manager_dn, {'userPassword': manager_pw})
        conn.strategy.add_entry(
            'uid=user0,ou=kubernetes,ou=people,o=test,c=de', {
                'userPassword': 'test123',
                'memberOf': ['cn=devops,ou=cloud,ou=people,o=test,c=de']
            })

        return conn


manager_user = 'manager'
manager_dn = 'uid=manager,ou=management,ou=people,o=test,c=de'
manager_pw = 'letsmanage'
# Create the AuthHandler instance with mocks
authHandler = AuthHandler(
    manager_dn, manager_pw,
    MockConnectionProvider()
)


class TestAuthHandler(unittest.TestCase):

    def test_validate_user_credentials_success(self):
        ret = authHandler.validate_user_credentials(manager_dn, manager_user, manager_pw, 'test')
        self.assertTrue(ret)

    def test_validate_user_credentials_failure(self):
        ret = authHandler.validate_user_credentials(manager_dn, manager_user, 'wrong-pw', 'test')
        self.assertFalse(ret)

    def test_validate_user_in_group_success(self):
        ldapParameters = [{
            'searchBase': 'ou=people,o=test,c=de',
            'requiredGroup': 'cn=devops,ou=cloud,ou=people,o=test,c=de'
        }]
        ret = authHandler.validate_user_in_group('user0', 'test', ldapParameters)
        self.assertEqual('uid=user0,ou=kubernetes,ou=people,o=test,c=de', ret)

    def test_validate_user_in_group_failure(self):
        ldapParameters = [{
            'searchBase': 'ou=people,o=test,c=de',
            'requiredGroup': 'cn=admin,ou=cloud,ou=people,o=test,c=de'
        }]
        # user is not in group
        ret = authHandler.validate_user_in_group('user0', 'test', ldapParameters)
        self.assertIsNone(ret)
        # user does not exist
        ret = authHandler.validate_user_in_group('user99', 'test', ldapParameters)
        self.assertIsNone(ret)

    def test_validate_success(self):
        ldapParameters = [{
            'searchBase': 'ou=people,o=test,c=de',
            'requiredGroup': 'cn=devops,ou=cloud,ou=people,o=test,c=de'
        }]
        ret = authHandler.validate('user0', 'test123', 'test', ldapParameters)
        self.assertTrue(ret)

    def test_validate_failure(self):
        ldapParameters = [{
            'searchBase': 'ou=people,o=test,c=de',
            'requiredGroup': 'cn=devops,ou=cloud,ou=people,o=test,c=de'
        }]
        ret = authHandler.validate('user0', 'wrong-pw', 'test', ldapParameters)
        self.assertFalse(ret)


if __name__ == '__main__':
    unittest.main()
