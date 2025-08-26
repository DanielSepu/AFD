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
    """
    Inserta una fila en SensorsData y VdfData con mediciones estables/realistas.
    - Mantiene una memoria interna para suavizar (por clave) entre llamadas.
    - Aplica variaciones pequeñas por tipo de variable y recortes por límites físicos.
    """
    base_sensors = get_base(sensor=True)
    base_vdf     = get_base(sensor=False)

    if not base_sensors or not base_vdf:
        logger_AFD.warning("Simulador inactivo o sin datos base, no se insertó nada.")
        return

    # ----------------- utilidades internas (sin dependencias externas) -----------------
    import random

    # memoria del suavizado por clave (se persiste entre invocaciones)
    if not hasattr(insert_sensor_data, "_last_values"):
        insert_sensor_data._last_values = {}
    _LAST = insert_sensor_data._last_values

    ALPHA_SMOOTH = 0.25  # menor => más estable

    def _smooth(key: str, new_value: float) -> float:
        prev = _LAST.get(key, new_value)
        val = ALPHA_SMOOTH * float(new_value) + (1.0 - ALPHA_SMOOTH) * float(prev)
        _LAST[key] = val
        return val

    def _percent_variation_for_key(key: str) -> float:
        """Porcentaje máx. de variación (±) según el tipo de sensor."""
        k = key.lower()
        if "barometr" in k:
            return 0.001   # ±0.1%
        if "temp" in k:
            return 0.02    # ±2%
        if "hum" in k:
            return 0.02    # ±2% HR
        if "presion" in k or "presión" in k or "estatic" in k or "total" in k:
            return 0.02    # ±2% presiones
        return 0.05        # por defecto ±5%

    def _absolute_variation_for_key(key: str) -> float | None:
        """Delta absoluto si aplica (si no, usar %)."""
        k = key.lower()
        if "rpm" in k:
            return 50.0    # ±50 rpm
        if "frecuencia" in k or "hz" in k:
            return 0.05    # ±0.05 Hz
        if "corriente" in k or "amp" in k or "amper" in k:
            return 0.05    # ±0.05 A
        if "volt" in k:
            return 0.5     # ±0.5 V
        return None

    def _vary(key: str, base_value: float) -> float:
        """Genera valor variado alrededor del base."""
        abs_delta = _absolute_variation_for_key(key)
        if abs_delta is not None:
            return base_value + random.uniform(-abs_delta, abs_delta)
        pct = _percent_variation_for_key(key)
        return base_value * (1.0 + random.uniform(-pct, pct))

    def _clip_by_key(key: str, value: float, base: float) -> float:
        """Recorte por límites físicos razonables."""
        k = key.lower()
        v = float(value)

        if "hum" in k:
            return max(0.0, min(100.0, v))
        if "temp" in k:
            return max(-40.0, min(80.0, v))
        if "barometr" in k:
            return max(80000.0, min(110000.0, v))
        if "presion" in k or "presión" in k or "estatic" in k or "total" in k:
            low = max(0.0, base * 0.7)
            high = max(low, base * 1.3)
            return min(max(v, low), high)
        if "rpm" in k:
            low = max(0.0, base - 500.0)
            high = max(low, base + 500.0)
            return min(max(v, low), high)
        return v

    def _stable_value(prefix: str, key: str, base_value: float) -> float:
        """Variación -> suavizado -> clip -> redondeo."""
        varied = _vary(key, base_value)
        smoothed = _smooth(f"{prefix}:{key}", varied)  # prefijos separan Sensors vs VDF
        clipped = _clip_by_key(key, smoothed, base_value)
        return round(clipped, 1) if abs(clipped) >= 1000 else round(clipped, 2)

    # ----------------- generación de registros -----------------
    now = timezone.now()

    # -------------- SensorsData -----------------
    sensores = {'ts': now}
    for k, v in base_sensors.items():
        try:
            base_val = float(v)
            sensores[k] = _stable_value("S", k, base_val)
        except Exception:
            # Campos no numéricos se dejan tal cual
            sensores[k] = v

    SensorsData.objects.using('sensorDB').create(**sensores)

    # -------------- VdfData ---------------------
    vdf = {'ts': now}
    for k, v in base_vdf.items():
        try:
            base_val = float(v)
            vdf[k] = _stable_value("V", k, base_val)
        except Exception:
            vdf[k] = v

    VdfData.objects.using('sensorDB').create(**vdf)

    logger_AFD.info(
        "Simulador: nuevo registro SensorsData y VdfData insertados a %s",
        now.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    )
