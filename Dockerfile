FROM python:3.7.9-alpine3.12

RUN pip install --no-cache-dir flask Flask-HTTPAuth ldap3 PyYAML gunicorn

COPY ./*.py /opt/
EXPOSE 9000
CMD gunicorn --chdir /opt/ --workers 1 --bind 0.0.0.0:9000 wsgi:app