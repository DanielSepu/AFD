import time
import random
from django.utils import timezone

from applications.getdata.models import SensorsData


# Valores base para simular datos reales
base_data = {
    'pt2': 1.2,
    'ps2': 0.9,
    'densidad2': 1.1,
    'q2': 12.0,
    'pt1': 1.3,
    'ps1': 1.0,
    'densidad1': 1.05,
    'q1': 10.5,
    'lc': 1.0,
    'qf': 8.0,
    'k': 0.98,
    'tbs': 22.5,
    'hr': 45.0,
    'tbh': 30.0,
    'tgbh': 100.0
}

def generate_variation(base_value, variation_range=0.05):
    """
    Genera una variación aleatoria en torno a un valor base.
    """
    return base_value + random.uniform(-variation_range, variation_range)

def insert_sensor_data(count = None):
    """
    Inserta un nuevo conjunto de datos en la base de datos cada 30 segundos.
    """
    print(f"-- insertando datos --")
    sensor_data = {
            'ts': timezone.now(),  # Marca de tiempo actual
            'pt2': generate_variation(base_data['pt2']),
            'ps2': generate_variation(base_data['ps2']),
            'densidad2': generate_variation(base_data['densidad2']),
            'q2': generate_variation(base_data['q2']),
            'pt1': generate_variation(base_data['pt1']),
            'ps1': generate_variation(base_data['ps1']),
            'densidad1': generate_variation(base_data['densidad1']),
            'q1': generate_variation(base_data['q1']),
            'lc': generate_variation(base_data['lc']),
            'qf': generate_variation(base_data['qf']),
            'k': generate_variation(base_data['k']),
            'tbs': generate_variation(base_data['tbs']),
            'hr': generate_variation(base_data['hr']),
            'tbh': generate_variation(base_data['tbh']),
            'tgbh': generate_variation(base_data['tgbh']),

        }

    # Crear una nueva instancia de SensorsData y guardarla en la base de datos
    SensorsData.objects.using('sensorDB').create(**sensor_data)


if __name__ == "__main__":
    insert_sensor_data()
