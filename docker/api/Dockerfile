FROM python:3.6

ARG REQ_FILE

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/mcod_backend

ADD . /usr/src/mcod_backend

RUN apt-get update && apt-get install -y gettext

COPY ./docker/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

COPY ./docker/api/start-api.sh /usr/local/bin/start-api
RUN chmod +x /usr/local/bin/start-api

COPY ./docker/api/start-admin.sh /usr/local/bin/start-admin
RUN chmod +x /usr/local/bin/start-admin

COPY ./docker/api/start-celery.sh /usr/local/bin/start-celery
RUN chmod +x /usr/local/bin/start-celery

COPY ./docker/api/run-tests.sh /usr/local/bin/run-tests
RUN chmod +x /usr/local/bin/run-tests

RUN pip install -r ${REQ_FILE}

RUN python manage.py compilemessages --settings mcod.settings.env_dev

EXPOSE 8000 8001

