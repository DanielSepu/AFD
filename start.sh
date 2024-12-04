#!/bin/bash


echo "Iniciando el servidor con Gunicorn..."
# Iniciar el servidor Django con Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8080 core.wsgi:application