release: python manage.py migrate --noinput --fake-initial && python manage.py loaddata_once
web: gunicorn myblog.wsgi --bind 0.0.0.0:$PORT
