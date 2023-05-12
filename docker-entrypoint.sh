#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --http :8080 --ini configurations/server.ini --static-map /static=static --static-map /favicon.ico=favicon.ico
