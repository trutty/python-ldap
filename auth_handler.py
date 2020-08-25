from ldap3 import Server, Connection, ServerPool, ROUND_ROBIN
from ldap3.core.exceptions import LDAPException
import logging

logging.basicConfig(format='[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s', level=logging.DEBUG)


class AuthHandler:

    def __init__(self, ldap_endpoints, dn_username, dn_password):
        self.ldapServers = ldap_endpoints
        self.dnUsername = dn_username
        self.dnPassword = dn_password

        logging.info("Configuring LDAP servers")
        self.server_pool = ServerPool(None, ROUND_ROBIN)
        for ldapServer in self.ldapServers:
            self.server_pool.add(Server(ldapServer))

    def validate_user_in_group(self, username, search_base, required_group):
        try:
            with Connection(self.server_pool, self.dnUsername, self.dnPassword, read_only=True) as conn:
                search_filter = '(&(uid={})(memberOf={}))'.format(username, required_group)
                conn.search(search_base, search_filter)
                if len(conn.response) == 1:
                    user_dn = conn.response[0]['dn']
                    logging.info("Found user '%s' in group '%s'", user_dn, required_group)
                    return user_dn
                else:
                    logging.error("Zero or multiple users found for '%s'", search_filter)

        except LDAPException as e:
            logging.error("Error while trying to lookup user. %s", e)

        return None

    def validate_user_credentials(self, user_dn, password):
        logging.info("Trying to authenticate '%s'", user_dn)
        conn = Connection(self.server_pool, user_dn, password, read_only=True, lazy=False, raise_exceptions=False)
        if conn.bind():
            logging.info("Supplied credential are valid for '%s'", user_dn)
            return True
        else:
            logging.error("Bind not successful for '%s'", user_dn)
            return False

    def validate(self, username, password, search_base, required_group):
        user_dn = self.validate_user_in_group(username, search_base, required_group)
        if user_dn is None:
            return False
        else:
            return self.validate_user_credentials(user_dn, password)
