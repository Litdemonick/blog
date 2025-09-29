release: python manage.py migrate && python manage.py loaddata backup.json && python manage.py collectstatic --noinput --clear
web: gunicorn myblog.wsgi --bind 0.0.0.0:8080
