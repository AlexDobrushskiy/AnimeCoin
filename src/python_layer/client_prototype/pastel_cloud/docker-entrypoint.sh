#!/bin/bash

# Collect static files
echo "Collect static files"
python /opt/app/manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python /opt/app/manage.py migrate

uwsgi --ini /opt/app/uwsgi.ini
