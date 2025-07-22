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

echo "📥 Insertando datos iniciales desde SQL..."
if command -v psql >/dev/null 2>&1 && [ -n "$DATABASE_URL" ]; then
    psql "$DATABASE_URL" -f init.sql
else
    echo "⚠️ Saltando inserción de datos: psql no disponible o DATABASE_URL no definido"
fi

echo "🚀 Iniciando Gunicorn..."
exec gunicorn miapp.wsgi:application --bind 0.0.0.0:8000