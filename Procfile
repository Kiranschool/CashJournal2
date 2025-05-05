release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn cashjournal.wsgi --log-file -
