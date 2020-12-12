import logging

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.DEBUG)


class AuthHandler:

    def __init__(self, manager_dn, manager_password, connection_provider):
        self.managerDn = manager_dn
        self.managerPassword = manager_password
        self.connectionProvider = connection_provider

    def validate_user_in_group(self, username, config, ldap_parameters):
        conn = self.connectionProvider.connection(self.managerDn, self.managerPassword)
        if conn.bind() is False:
            logging.error("[user=%s, config=%s] Error while trying to connect to LDAP server(s)", username, config)
            return None

        try:
            for ldap_parameter in ldap_parameters:
                search_base = ldap_parameter['searchBase']
                group = ldap_parameter['requiredGroup']

                search_filter = '(&(uid={})(memberOf={}))'.format(username, group)
                conn.search(search_base, search_filter)
                if len(conn.response) == 1:
                    user_dn = conn.response[0]['dn']
                    logging.info("[user=%s, config=%s] '%s' found in group '%s'", username, config, user_dn, group)
                    return user_dn

        finally:
            conn.unbind()

        groups = [ldap_parameter['requiredGroup'] for ldap_parameter in ldap_parameters]
        logging.warning("[user=%s, config=%s] user not in LDAP or not in required group(s) %s",
                        username, config, groups)
        return None

    def validate_user_credentials(self, user_dn, username, password, config):
        conn = self.connectionProvider.connection(user_dn, password)
        if conn.bind():
            logging.info("[user=%s, config=%s] authentication successful", username, config)
            conn.unbind()
            return True
        else:
            logging.warning("[user=%s, config=%s] authentication not successful", username, config)
            return False

    def validate(self, username, password, ldap_config_key, ldap_parameters):
        user_dn = self.validate_user_in_group(username, ldap_config_key, ldap_parameters)
        if user_dn is None:
            return False
        else:
            return self.validate_user_credentials(user_dn, username, password, ldap_config_key)
