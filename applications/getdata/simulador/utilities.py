import random
from django.utils import timezone
from core.logger_config import logger_AFD
from applications.getdata.models import SensorsData, VdfData
from applications.getdata.models import Simulador

def get_active_simulator():
    return (
        Simulador.objects
        .filter(estado=True)
        .order_by('-id')
        .first()
    )

def get_base(sensor=True):
    """
    Devuelve el diccionario de valores base correspondiente.
    - sensor=True  -> toma 'sensors_data'
    - sensor=False -> toma 'vdf_data'
    """
    sim = get_active_simulator()
    if not sim:
        return {}

    key = 'sensors_data' if sensor else 'vdf_data'
    base_dict = sim.data.get(key, {})
    # Quitamos el 'ts' si viene en el JSON
    base_dict.pop('ts', None)
    return base_dict




def gen_variation(base, rng=0.001):
    """Pequeña variación absoluta; para rpm usamos ±50."""
    if base is None:
        return None
    return base + random.uniform(-rng, rng)

def insert_sensor_data():
    base_sensors = get_base(sensor=True)
    base_vdf     = get_base(sensor=False)

    if not base_sensors or not base_vdf:
        logger_AFD.warning("Simulador inactivo o sin datos base, no se insertó nada.")
        return

    # -------------- SensorsData -----------------
    sensores = {
        'ts': timezone.now(),
        **{k: gen_variation(v) for k, v in base_sensors.items()}
    }
    SensorsData.objects.using('sensorDB').create(**sensores)

    # -------------- VdfData ---------------------
    vdf = {
        'ts': timezone.now(),
        **{
            k: gen_variation(v, rng=50 if k == 'rpm' else 0.001)
            for k, v in base_vdf.items()
        }
    }
    VdfData.objects.using('sensorDB').create(**vdf)

    logger_AFD.info(
        "Simulador: nuevo registro SensorsData y VdfData insertados a %s",
        sensores['ts'].astimezone().strftime("%Y-%m-%d %H:%M:%S")
    )
