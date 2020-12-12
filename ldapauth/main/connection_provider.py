from ldap3 import Server, Connection, ServerPool, ROUND_ROBIN


class ConnectionProvider:

    def __init__(self, ldap_servers):
        self.serverPool = ServerPool(None, ROUND_ROBIN)
        for ldapServer in ldap_servers:
            self.serverPool.add(Server(ldapServer))

    def connection(self, user_dn, password):
        return Connection(self.serverPool, user_dn, password, read_only=True, lazy=False, raise_exceptions=False)
