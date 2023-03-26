#!/bin/bash

set -e

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Make database migrations"
python manage.py makemigrations --noinput

echo "Apply database migrations"
python manage.py migrate

if [ "$ENV" == "dev" ]
then
  echo "Running Development"
  python manage.py runserver 0.0.0.0:8000
else
  echo "Running Production"
  gunicorn octoincore.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
fi
