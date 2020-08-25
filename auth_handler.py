from ldap3 import Server, Connection, ServerPool, ROUND_ROBIN
from ldap3.core.exceptions import LDAPException
import logging

logging.basicConfig(format='[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s', level=logging.DEBUG)


class AuthHandler:

    def __init__(self, ldap_servers, dn_username, dn_password):
        self.ldapServers = ldap_servers
        self.dnUsername = dn_username
        self.dnPassword = dn_password

        logging.info("Configuring LDAP servers")
        self.server_pool = ServerPool(None, ROUND_ROBIN)
        for ldapServer in self.ldapServers:
            self.server_pool.add(Server(ldapServer))

    def validate_user_in_group(self, username, ldap_parameters):
        try:
            with Connection(self.server_pool, self.dnUsername, self.dnPassword, read_only=True) as conn:
                for ldap_parameter in ldap_parameters:
                    search_base = ldap_parameter['searchBase']
                    required_group = ldap_parameter['requiredGroup']

                    search_filter = '(&(uid={})(memberOf={}))'.format(username, required_group)
                    conn.search(search_base, search_filter)
                    if len(conn.response) == 1:
                        user_dn = conn.response[0]['dn']
                        logging.info("Found user '%s' in group '%s'", user_dn, required_group)
                        return user_dn

        except LDAPException as e:
            logging.error("Error while trying to lookup user. %s", e)
            return None

        logging.info("User '%s' not found")
        return None

    def validate_user_credentials(self, user_dn, password):
        conn = Connection(self.server_pool, user_dn, password, read_only=True, lazy=False, raise_exceptions=False)
        if conn.bind():
            logging.info("Credentials are valid for '%s'", user_dn)
            conn.unbind()
            return True
        else:
            logging.error("Bind not successful for '%s'", user_dn)
            return False

    def validate(self, username, password, ldap_parameters):
        user_dn = self.validate_user_in_group(username, ldap_parameters)
        if user_dn is None:
            return False
        else:
            return self.validate_user_credentials(user_dn, password)
