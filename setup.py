import os
import sys

# Añade el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Establece la variable de entorno para la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()
