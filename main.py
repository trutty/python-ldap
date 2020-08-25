from flask import Flask
from flask import request
from flask_httpauth import HTTPBasicAuth
from auth_handler import AuthHandler
from cache import Cache
from os import environ
from yaml import safe_load
import logging

logging.basicConfig(format='%(asctime)s %(process)d %(levelname)s %(message)s', level=logging.DEBUG)

# Init flask app
app = Flask(__name__)
auth = HTTPBasicAuth()

# Connect to memcached
CACHE_EXPIRATION = 10  # Expiration in minutes
cache = Cache(CACHE_EXPIRATION)

# Init LDAP config
with open("/config/config.yaml", 'r') as stream:
    config = safe_load(stream)

# Create the AuthHandler instance
authHandler = AuthHandler(
    config['ldapServers'],
    environ['LDAP_MANAGER_BINDDN'],
    environ["LDAP_MANAGER_PASSWORD"],
)


@auth.verify_password
def login(username, password):

    # Check if username or password is empty
    if not username or not password:
        return False

    # Check if username is cached and has same password
    if cache.validate(username, password):
        logging.info("Successful cache hit for '%s'", username)
        return True

    # Get headers from request
    searchBase = request.headers['Ldap-User-BaseDN']
    requiredGroup = request.headers['Ldap-Required-Group']
    # The username and password are from the Basic Authentication pop-up form
    if authHandler.validate(username, password, searchBase, requiredGroup):
        # Include the user in the cache
        cache.add(username, password)
        return True

    return False


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@auth.login_required
def index(path):
    code = 200
    msg = "LDAP Authentication"
    headers = []
    return msg, code, headers


# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)
