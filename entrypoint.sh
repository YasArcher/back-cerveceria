#!/bin/sh

echo "🗑️ Eliminando migraciones existentes..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo "Creando migraciones..."
python manage.py makemigrations usuarios cervezas --noinput

echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

echo "🎯 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "📥 Insertando datos iniciales..."
python manage.py loaddata init_data.json

echo "🚀 Iniciando Gunicorn..."
exec gunicorn miapp.wsgi:application --bind 0.0.0.0:8000