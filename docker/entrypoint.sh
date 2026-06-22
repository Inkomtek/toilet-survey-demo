#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.5
done
echo "PostgreSQL is up."

python manage.py makemigrations core --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_reasons
python manage.py seed_actions

exec gunicorn server.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3