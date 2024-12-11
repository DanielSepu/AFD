#!/bin/bash

# Obtener el usuario actual del sistema operativo
USER=$(whoami)
PROJECT_DIR="/home/$USER/AFD"
SERVICE_NAME="AFD"
GUNICORN_BIND="0.0.0.0:8080"
GUNICORN_WORKERS=3

# Crear un archivo de servicio systemd para Gunicorn
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Creando el archivo de servicio para Gunicorn en $SERVICE_FILE"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Gunicorn service for VDF app
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/manage.py runserver 0.0.0.0:8080
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Recargar systemd para aplicar los cambios
echo "Recargando systemd y habilitando el servicio..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Verificar el estado del servicio
sudo systemctl status $SERVICE_NAME
