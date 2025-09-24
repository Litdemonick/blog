release: python manage.py migrate && python manage.py collectstatic --noinput --clear
web: gunicorn myblog.wsgi