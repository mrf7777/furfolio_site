#!/bin/bash
RUN_PORT="8000"

/opt/venv/bin/python manage.py migrate --no-input
/opt/venv/bin/gunicorn furfolio_site.wsgi --worker-tmp-dir /dev/shm --bind "0.0.0.0:${RUN_PORT}" --daemon

nginx -g 'daemon off;'
