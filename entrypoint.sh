#!/bin/bash
# entrypoint.sh

echo "👉 Aplicando migraciones..."
python manage.py migrate --noinput

if [ -f "backup.json" ]; then
    echo "👉 Cargando datos iniciales desde backup.json..."
    python manage.py loaddata backup.json || echo "⚠️ No se pudo cargar backup.json"
fi

echo "👉 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "👉 Levantando servidor Gunicorn..."
exec gunicorn myblog.wsgi --bind 0.0.0.0:8080
