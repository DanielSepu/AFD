import time
import random
from django.utils import timezone

from applications.getdata.models import SensorsData, VdfData

# Valores base para simular datos reales en SensorsData
base_data = {
    'pt2': 1450,
    'ps2': 1180,
    'densidad2': 90000,
    'q2': 80,
    'pt1': 1920,
    'ps1': 1610,
    'densidad1': 1.1,
    'q1': 20,
    'lc': 27,
    'qf': 15,
    'k': 0,
    'tbs': 29,
    'hr': 70,
    'tbh': 0,
    'tgbh': 100.0
}



# Valores base para simular datos reales en VdfData
base_data_vdf = {
    'fref': 50.0,  # Frecuencia de referencia en Hz
    'freal': 50.0,  # Frecuencia real en Hz
    'vf': 120.0,  # Voltaje (V)
    'oc': 1.0,  # Corriente de operación (A)
    'power': 15.0,  # Potencia (kW)
    'powerc': 14.8,  # Potencia corregida (kW)
    'rpm': 1500.0  # RPM base del ventilador
}

def generate_variation(base_value, variation_range=0.0001):
    """
    Genera una variación aleatoria en torno a un valor base.
    """
    return base_value + random.uniform(-variation_range, variation_range)

def insert_sensor_data(count=None):
    """
    Inserta un nuevo conjunto de datos en las tablas SensorsData y VdfData.
    """
    print(f"-- Insertando datos SensorsData y VdfData --")
    
    # Inserción de datos en SensorsData
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
    
    # Guardar la instancia de SensorsData en la base de datos
    SensorsData.objects.using('sensorDB').create(**sensor_data)

    # Inserción de datos en VdfData
    vdf_data = {
        'ts': timezone.now(),  # Marca de tiempo actual
        'fref': generate_variation(base_data_vdf['fref']),  # Variación de frecuencia de referencia
        'freal': generate_variation(base_data_vdf['freal']),  # Variación de frecuencia real
        'vf': generate_variation(base_data_vdf['vf']),  # Variación del voltaje
        'oc': generate_variation(base_data_vdf['oc']),  # Variación de la corriente
        'power': generate_variation(base_data_vdf['power']),  # Variación de la potencia
        'powerc': generate_variation(base_data_vdf['powerc']),  # Variación de la potencia corregida
        'rpm': generate_variation(base_data_vdf['rpm'], variation_range=50)  # Variación en RPM con un rango mayor
    }

    # Guardar la instancia de VdfData en la base de datos
    VdfData.objects.using('sensorDB').create(**vdf_data)

if __name__ == "__main__":
    insert_sensor_data()
