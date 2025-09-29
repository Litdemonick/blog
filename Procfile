release: python manage.py migrate --noinput
web: gunicorn myblog.wsgi --bind 0.0.0.0:8080
