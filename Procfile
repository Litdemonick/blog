release: python manage.py migrate && python manage.py loaddata backup.json
web: gunicorn myblog.wsgi --bind 0.0.0.0:$PORT
