FROM python:3.9-alpine

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ldapauth/main/*.py /opt/

# run as non-root user
RUN addgroup -S ldap && adduser -S -g ldap -u 1000 ldap
USER 1000

EXPOSE 9000
CMD gunicorn --chdir /opt/ --workers 1 --bind 0.0.0.0:9000 wsgi:app