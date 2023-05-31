#!/usr/bin/env bash

if [ -z "${PORT}" ]
then
  PORT=8080
fi

python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --http :$PORT --ini configurations/server.ini --static-map /static=static --static-map /favicon.ico=favicon.ico
