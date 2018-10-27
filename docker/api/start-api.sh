#!/usr/bin/env bash

set -e

flag=0
retries=0
max_retries=2
sleep_time=3
while [ $flag -eq 0 ]; do
    if [ $retries -eq $max_retries ]; then
        echo Executed $retries retries, aborting
        exit 1
    fi
    sleep $sleep_time
    if [ "$POSTGRES_HOST_TYPE" == "machine" ]; then
        python manage.py migrate
        gunicorn mcod.api:app --bind $API_WSGI_HOST:$API_WSGI_PORT --reload -R --env PYTHONUNBUFFERED=1 -k gevent
    else
        wait-for-it $POSTGRES_HOST:$POSTGRES_PORT -s --timeout=10 -- python manage.py migrate
        wait-for-it $POSTGRES_HOST:$POSTGRES_PORT -s --timeout=10 -- gunicorn mcod.api:app --bind $API_WSGI_HOST:$API_WSGI_PORT --reload -R --env PYTHONUNBUFFERED=1 -k gevent
    fi
    if [ $? -eq 0 ]; then
        flag=1
    else
        echo "Cannot start api, retrying in $sleep_time seconds..."
        let retries++
    fi
done

