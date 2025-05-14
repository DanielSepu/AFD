#!/bin/bash

# Variables personalizables
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_NAME="postgres"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Verificar si el usuario tiene permisos sudo
if [ "$EUID" -ne 0 ]; then
    echo "Por favor, ejecuta este script como superusuario (sudo)."
    exit
fi

echo "Actualizando paquetes e instalando dependencias..."
apt update -y && apt upgrade -y
apt install -y postgresql postgresql-contrib python3 python3-venv python3-pip gunicorn

echo "Configurando PostgreSQL..."
# Iniciar el servicio PostgreSQL
systemctl enable postgresql
systemctl start postgresql

# Crear usuario y base de datos en PostgreSQL
sudo -u postgres psql <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

echo "Base de datos '$DB_NAME' y usuario '$DB_USER' creados con éxito."

echo "Configurando entorno virtual..."
# Crear el entorno virtual
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

# Activar el entorno virtual
source $VENV_DIR/bin/activate

echo "Instalando dependencias..."
# Instalar requerimientos desde requirements.txt
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r $REQUIREMENTS_FILE 

else
    echo "Archivo $REQUIREMENTS_FILE no encontrado. Asegúrate de tenerlo en el directorio actual."
    deactivate
    exit 1
fi

echo "Configurando variables de entorno desde .env..."
# Cargar variables del archivo .env (si existe)
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Archivo .env no encontrado. Asegúrate de tenerlo en el directorio actual."
    deactivate
    exit 1
fi

echo "Migrando base de datos de Django..."
# Ejecutar migraciones de Django
python manage.py migrate

echo "Colectando archivos estáticos..."
# Colectar archivos estáticos
python manage.py collectstatic --noinput

echo "Iniciando el servidor con Gunicorn..."
# Iniciar el servidor Django con Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8080 core.wsgi:application

# Desactivar entorno virtual al finalizar
deactivate

echo "Proceso completado. El servidor está corriendo en el puerto 8080."
