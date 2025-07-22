#!/bin/sh

echo "Creando migraciones..."
python manage.py makemigrations --noinput

echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

echo "🎯 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "📥 Insertando datos iniciales desde SQL..."
# Ejecuta solo si psql está instalado y la variable DATABASE_URL está definida
if command -v psql >/dev/null 2>&1 && [ -n "$DATABASE_URL" ]; then
    psql "$DATABASE_URL" -f init.sql
else
    echo "⚠️ Saltando inserción de datos: psql no disponible o DATABASE_URL no definido"
fi

echo "🚀 Iniciando Gunicorn..."
exec gunicorn miapp.wsgi:application --bind 0.0.0.0:8000
