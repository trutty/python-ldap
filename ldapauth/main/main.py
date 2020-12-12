from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from auth_handler import AuthHandler
from cache import Cache
from os import environ
from yaml import safe_load
import logging

from connection_provider import ConnectionProvider

# init logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.DEBUG)

# Init flask app
app = Flask(__name__)
auth = HTTPBasicAuth()

# Basic cache
CACHE_KEY_EXPIRATION_SECONDS = 60 * 60 * 8  # 8 hours
cache = Cache(CACHE_KEY_EXPIRATION_SECONDS)

# Init LDAP config
with open("/config/config.yaml", 'r') as stream:
    config = safe_load(stream)

# Create the AuthHandler instance
authHandler = AuthHandler(
    environ['LDAP_MANAGER_BINDDN'],
    environ["LDAP_MANAGER_PASSWORD"],
    ConnectionProvider(config['ldapServers'])
)


@auth.verify_password
def login(username, password):
    # Check if username or password is empty
    if not username or not password:
        return False

    # Get lookup key for config
    ldap_config_key = request.headers['Ldap-Config-Key']
    # Check if authentication was cached
    if cache.validate(username, ldap_config_key, password):
        logging.info("[user=%s, config=%s] authenticated from cache", username, ldap_config_key)
        return True

    # Lookup LDAP config
    ldapParameters = config[ldap_config_key]
    # Validate user
    if authHandler.validate(username, password, ldap_config_key, ldapParameters):
        # Add successful authentication to cache
        cache.set(username, ldap_config_key, password)
        return True

    return False


@app.route('/')
@auth.login_required
def index():
    code = 200
    msg = "LDAP Authentication"
    headers = []
    return msg, code, headers


# health endpoint
@app.route('/health')
def health():
    if cache is None or authHandler is None:
        return "not healthy", 503
    else:
        return "healthy", 200


# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)
