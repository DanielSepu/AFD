import time
import random
from django.utils import timezone
from core.logger_config import logger_AFD
from applications.getdata.models import SensorsData, VdfData

# Valores base para simular datos reales en SensorsData
base_data = {
    'pt2': 488,
    'ps2': 271,
    'Pbs2': 95362,         # ex densidad2
    'Tbs2': 30.5,          # ex q2
    'HRs2': 34.5,          # ex pt1
    'pt1': 709,            # ex ps1
    'ps1': 490,            # ex densidad1
    'Pbs1': 95362,         # ex q1
    'Tbs1': 30.7,          # ex lc
    'HRs1': 37.2,          # ex qf
    'k': 0,
    'tbs': 0,
    'hr': 0,
    'tbh': 0,
    'tgbh': 0
}


# Valores base para simular datos reales en VdfData
base_data_vdf = {
    'fref': 50.0,  # Frecuencia de referencia en Hz
    'freal': 50.0,  # Frecuencia real en Hz
    'vf': 120.0,  # Voltaje (V)
    'oc': 1.0,  # Corriente de operación (A)
    'power': 15.0,  # Potencia (kW)
    'powerc': 14.8,  # Potencia corregida (kW)
    'rpm': 3000.0  # RPM base del ventilador
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
    
    # Inserción de datos en SensorsData
    sensor_data = {
        'ts': timezone.now(),  # Marca de tiempo actual
        'pt2': generate_variation(base_data['pt2']),
        'ps2': generate_variation(base_data['ps2']),
        'Pbs2': generate_variation(base_data['Pbs2']),  # ex densidad2
        'Tbs2': generate_variation(base_data['Tbs2']),  # ex q2
        'HRs2': generate_variation(base_data['HRs2']),  # ex pt1
        'pt1': generate_variation(base_data['pt1']),    # ex ps1
        'ps1': generate_variation(base_data['ps1']),    # ex densidad1
        'Pbs1': generate_variation(base_data['Pbs1']),  # ex q1
        'Tbs1': generate_variation(base_data['Tbs1']),  # ex lc
        'HRs1': generate_variation(base_data['HRs1']),  # ex qf
        'k': generate_variation(base_data['k']),
        'tbs': generate_variation(base_data['tbs']),
        'hr': generate_variation(base_data['hr']),
        'tbh': generate_variation(base_data['tbh']),
        'tgbh': generate_variation(base_data['tgbh']),
    }
    
    # Guardar la instancia de SensorsData en la base de datos
    # SensorsData.objects.using('sensorDB').create(**sensor_data)

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
    # VdfData.objects.using('sensorDB').create(**vdf_data)

if __name__ == "__main__":
    insert_sensor_data()
