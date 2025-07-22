# Usa una imagen ligera de Python 3.11
FROM python:3.11-slim

# Evita archivos pyc y buffer en consola
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crea directorio de trabajo
WORKDIR /code

# Instala dependencias del sistema necesarias (PostgreSQL, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Copia el archivo de requerimientos y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Recolecta archivos estáticos (si usas STATIC_ROOT)
RUN python manage.py collectstatic --noinput || true

# Expón el puerto usado por Gunicorn
EXPOSE 8000

# Configura la base de datos (si es necesario)
RUN python manage.py migrate


# Ejecuta Gunicorn como servidor WSGI
CMD ["gunicorn", "miapp.wsgi:application", "--bind", "0.0.0.0:8000"]
