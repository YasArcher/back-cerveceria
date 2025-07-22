# Usa una imagen ligera de Python 3.11
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Instala dependencias del sistema necesarias (PostgreSQL, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Copia el archivo de requerimientos e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Copia y da permisos al script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expón el puerto 8000
EXPOSE 8000

# Ejecuta el script
CMD ["/entrypoint.sh"]
