#!/bin/sh

echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

echo "🎯 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "📥 Insertando datos iniciales desde SQL..."
psql "$DATABASE_URL" -f init.sql

echo "🚀 Iniciando Gunicorn..."
exec gunicorn miapp.wsgi:application --bind 0.0.0.0:8000
