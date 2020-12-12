from datetime import datetime, timedelta
import hashlib


class Cache:
    def __init__(self, key_expiration_in_seconds):
        self.expirationInSeconds = key_expiration_in_seconds
        self.cache = {}

    @staticmethod
    def __key(username, ldap_config_key):
        return username + '#' + ldap_config_key

    @staticmethod
    def __value(password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Set cache entry for key
    def set(self, username, ldap_config_key, password):
        key = self.__key(username, ldap_config_key)
        value = self.__value(password)

        self.cache.update({key: {
            'validUntil': datetime.now() + timedelta(seconds=self.expirationInSeconds),
            'value': value
        }})

    # Validate if the cache key has the same value and is still valid
    def validate(self, username, ldap_config_key, password):
        key = self.__key(username, ldap_config_key)

        if key in self.cache:
            entry = self.cache.get(key)
            value = self.__value(password)
            if datetime.now() < entry['validUntil'] and entry['value'] == value:
                return True

        return False
