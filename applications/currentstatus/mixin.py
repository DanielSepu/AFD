from django.db.models import Max
from applications.currentstatus.tools import (
    area_ducto_circular, 
    area_inlet_bell, 
    calculate_perdida_choque_codos
)
from applications.currentstatus.utils import (
    caudal_aire_sensor1, 
    caudal_de_la_frente, 
    velocidad_aire_sensor
)
from applications.fanreal.fanAdministrator import FanAdministrator
from applications.getdata.models import Historial, Proyecto, SensorsData, VdfData
from applications.home.functions import get_last_project
from modules.semaforo import Semaforo
from django.contrib import messages



# Función para obtener el último registro de un modelo dado
def get_latest_record(model, using_db='sensorDB'):
    latest = model.objects.using(using_db).aggregate(Max('id'))
    max_id = latest['id__max']
    return model.objects.using(using_db).get(id=max_id)

# Obtiene el último proyecto
def get_current_project():
    return Proyecto.objects.all().order_by('id').last()

# Calcula la densidad y devuelve la densidad configurada, la calculada y su mitad
def compute_density( project, sensor_data, request=None):
    dens_configurada = sensor_data.ps1
    try:
        fan = FanAdministrator(project=project)
        dens_calculada = fan.densidad_aire_sensores['sensor1']
    except Exception as e:
        if request != None:
            print(f"imprimiendo request")
            messages.warning(request, e)
        else:
            print(f"Warning: {e}")   
        dens_calculada = 0
    mid_densidad = dens_calculada / 2
    return dens_configurada, mid_densidad, dens_calculada

# Configura el semáforo y calcula caudales
def setup_semaforo(project, sensor_data):
    fan = FanAdministrator(project)
    semaforo = Semaforo(fan=fan)
    semaforo.encender(project)
    Q1 = semaforo.calculate_Q1()
    Q2 = semaforo.calculate_Q2()
    leakage = semaforo.leakage_coefficient_v4()
    # Qf = caudal_de_la_frente(Q2, leakage, sensor_data.pt2, project.ducto.Ldsf)
    Qf = semaforo.calcular_qf(Q2, leakage, sensor_data.pt2, project.ducto.Ldsf)

    return semaforo, Q1, Qf

# Calcula las áreas relevantes
def compute_area_values(project):
    area_inlet = area_inlet_bell(project)
    area_ventilador = 3.14159 * (project.ventilador.amm / 2000) ** 2
    return area_inlet, area_ventilador

# Calcula las presiones dinámicas en entrada y ventilador
def compute_dynamic_pressures(mid_densidad, Q1, area_inlet, area_ventilador):
    presion_dinamica_entrada = mid_densidad * Q1**2 / (area_inlet ** 2)
    presion_dinamica_ventilador = mid_densidad * Q1**2 / (area_ventilador ** 2)
    return presion_dinamica_entrada, presion_dinamica_ventilador

# Suma la pérdida de choque de cada accesorio
def compute_sumatoria_choque(caracteristicas, presion_dinamica_entrada):
    return sum(c.factor_choque * presion_dinamica_entrada for c in caracteristicas)

# Calcula la pérdida de choque en la salida del ducto según el tipo
def compute_perdida_choque_salida(project, mid_densidad, Qf):
    try:
        area_ducto_circ = area_ducto_circular(project)
    except TypeError as e:
        raise TypeError(f"No se pudo realizar el cálculo: {e}, verifique el valor de diámetro del ducto")
    
    perdida_circular = mid_densidad * (Qf ** 2 / (area_ducto_circ ** 2))
    perdida_ovalado = mid_densidad * (Qf ** 2) / (project.ducto.area ** 2)
    
    if project.ducto.t_ducto == "ovalado":
        return perdida_ovalado
    elif project.ducto.t_ducto == "circular":
        return perdida_circular
    else:
        raise ValueError("No se pudo identificar el tipo de ducto")

# Suma las pérdidas totales del sistema
def compute_total_losses(perdida_choque_codos, sumatoria_choque_accesorios, perdida_choque_salida):
    return perdida_choque_codos + sumatoria_choque_accesorios + perdida_choque_salida

# Calcula presión estática, presión dinámica y pérdidas friccionales
def compute_static_and_friction(item_sensors, presion_dinamica_entrada, perdida_total):
    presion_total = item_sensors.pt1
    presion_estatica = round(presion_total - presion_dinamica_entrada, 0)
    presion_dinamica = item_sensors.pt1 - item_sensors.ps1
    var_intermedia = presion_total - presion_dinamica
    perdidas_friccionales = var_intermedia - perdida_total
    return presion_estatica, presion_dinamica, perdidas_friccionales

# Construye el diccionario de datos para la respuesta
def build_data_dict(item_sensors, item_vdf, project, Qf):
    fan = FanAdministrator(project=project)
    data = {
        "pt1": round(item_sensors.pt1, 2),
        "qf": round(Qf, 2),
        "q1": caudal_aire_sensor1(
                velocidad_aire_sensor(item_sensors.pt1 - item_sensors.ps1, fan.densidad_del_aire_s1()),
                project.ducto.area
            ),
        "HRs2": round(item_sensors.HRs2, 2),
        "densidad1": round(item_sensors.ps1, 2),
        "powerc": round(item_vdf.powerc, 2),
        "fref": round(item_vdf.fref, 2),
        "frequency_ratio_1": round((item_vdf.freal / item_vdf.fref) * 100, 2),
        "frequency_ratio_2": round((item_vdf.freal / item_vdf.fref) * 100, 2),
        "powerc_duplicate": round(item_vdf.powerc, 2),
    }
    return data

# Función que recibe un diccionario y retorna uno consolidado,
# eliminando claves repetidas y las entradas consideradas innecesarias.
def merge_detalle_semaforo(detalle):

    # Eliminar claves de nivel superior que no se desean
    for k in ['sensor', 'vdf', 'colores']:
        detalle.pop(k, None)
    merged = {}
    innecesarias = ['color', 'nivel_carga', 'presion_maxima', 'formula', 'Area_galeria', 'min', 'max']
    
    for key, subdict in detalle.items():
        if isinstance(subdict, dict):
            for subkey, value in subdict.items():
                if subkey.lower() in innecesarias:
                    continue
                if subkey in merged and merged[subkey] == value:
                    continue
                merged[subkey] = value
        else:
            if key.lower() in innecesarias:
                continue
            if key not in merged:
                merged[key] = subdict
    return merged

# Función para guardar en el modelo Historial usando el diccionario consolidado.
def guardar_historial_detalle(detalle):
    """
    Recibe el diccionario consolidado 'detalle' y crea una nueva instancia de Historial
    asignando los valores correspondientes a cada campo.
    """
    
    # logger_config.logger_AFD.debug(f"guardando historial v3: {detalle['v3']}")
    historial = Historial.objects.create(
        # Pérdidas de ductos
        pc1_dc   = detalle.get("perdida_choque_codos", 0.0),
        pc2_dc   = detalle.get('perdida_choque_codos'),  
        pc345_dc = 0.0,
        pcc_dc   = detalle.get("sumatoria_choque_accesorios", 0.0),

        # Fórmulas (se dejan en 0.0; actualiza si cuentas con valores)
        f1     = 0.0,
        f2_dc  = 0.0,
        f2_do  = 0.0,

        # Caudales
        q_c1   = detalle.get("caudal_del_ventilador", 0.0),
        q_c2   = 0.0,
        q_c345 = 0.0,
        q1     = detalle.get("q1", detalle.get("Q1", 0.0)),
        qf     = detalle.get("Qf", detalle.get("qf", 0.0)),

        # Otras pérdidas y presiones
        pct_sys = detalle.get("perdida_choque_total_sistema_ducto", 0.0),
        pd_v    = detalle.get("Presion_dinamica_ventilador_Pa", 0.0),
        pe_v    = detalle.get("presion_estatica", 0.0),
        pd_e    = detalle.get("presion_dinamica_entrada_Pa", 0.0),
        pcs_dc  = detalle.get("perdida_choque_salida_ducto", 0.0),
        tbs     = detalle['velocidad_sensor'].get("tbs"),
        tbh     = detalle['velocidad_sensor'].get("tbh2"),
        presion_t = detalle['v5'].get("presion_maxima"),
        pta_v   = 0.0,
        lc   = detalle.get("Lc", 0.0),
        tgbh   = detalle.get("tgbh", 0.0),
    )
    # logger_AFD.debug("Campos guardados en el historial:")
    for field in Historial._meta.get_fields():
        field_name = field.name
        if hasattr(historial, field_name):
            field_value = getattr(historial, field_name)
            # logger_AFD.debug(f"{field_name}: {field_value}")
    return historial

# Función principal que orquesta el procesamiento, consolidación y almacenamiento.
def procesar_datos_sensores(request=None):
    variables = {}

    # Obtener los últimos registros de sensores y VDF
    item_sensors = get_latest_record(SensorsData, using_db='sensorDB')
    item_vdf = get_latest_record(VdfData, using_db='sensorDB')
    
    # Obtener el proyecto actual y características del ventilador
    project = get_current_project()
    caracteristicas = project.ventilador.accesorios.all()
    variables.update({
        'vmm': project.ventilador.vmm,
        'amm': project.ventilador.amm,
        'nmm': project.ventilador.nmm,
        'densidad': item_sensors.ps1,
    })
    
    # Calcular densidad
    if request != None:
        _, mid_densidad, dens_calculada = compute_density( project, item_sensors, request=request)
    else:
        _, mid_densidad, dens_calculada = compute_density( project, item_sensors)
    
    # Configurar semáforo y caudales
    semaforo, Q1, Qf = setup_semaforo(project, item_sensors)
    variables['caudal_del_ventilador'] = Q1
    
    # Calcular áreas
    area_inlet, area_ventilador = compute_area_values(project)
    variables['area_inlet_bell_val'] = area_inlet
    variables['Area_ventilador'] = area_ventilador
    
    # Calcular presiones dinámicas
    presion_dinamica_entrada, presion_dinamica_ventilador = compute_dynamic_pressures(
        mid_densidad, Q1, area_inlet, area_ventilador
    )
    variables['presion_dinamica_entrada_Pa'] = presion_dinamica_entrada
    variables['Presion_dinamica_ventilador_Pa'] = presion_dinamica_ventilador
    
    # Pérdida de choque por accesorios
    sumatoria_choque_accesorios = compute_sumatoria_choque(caracteristicas, presion_dinamica_entrada)
    variables['sumatoria_choque_accesorios'] = sumatoria_choque_accesorios
    
    total_codos = project.codos
    try:
        _, perdidas_choque_codos = calculate_perdida_choque_codos(
            total_codos=total_codos, 
            mid_densidad=mid_densidad, 
            Q1=Q1,
            project=project, 
            Qf=Qf
        )
        variables["perdida_choque_codos"] = perdidas_choque_codos
    except TypeError as e:
        return {
            "status": "error",
            "message": f"No se pudo realizar el cálculo de choque de codos: {e}, verifique el valor de diámetro del ducto"
        }
    
    # Pérdida de choque en la salida del ducto
    try:
        perdida_choque_salida = compute_perdida_choque_salida(project, mid_densidad, Qf)
    except TypeError as e:
        return {
            "status": "error",
            "message": f"No se pudo realizar el cálculo: {e}, verifique el valor de diámetro del ducto"
        }
    variables['perdida_choque_salida_ducto'] = perdida_choque_salida
    variables['perdida_choque_salida_ducto2'] = perdida_choque_salida
    
    # Total de pérdidas
    perdida_total = compute_total_losses(perdidas_choque_codos, sumatoria_choque_accesorios, perdida_choque_salida)
    variables['perdida_choque_total_sistema_ducto'] = round(perdida_total,2)
    
    # Cálculo de presión estática y pérdidas friccionales
    presion_estatica, presion_dinamica, perdidas_friccionales = compute_static_and_friction(
        item_sensors, presion_dinamica_entrada, perdida_total
    )
    fan = FanAdministrator(project=project)
    # Calcular velocidad y caudal a partir de sensores
    velocidad_sensor = fan.velocidad_aire_sensores['sensor1']
    
    data = build_data_dict(
        item_sensors, item_vdf, project, Qf
    )
    
    # Se arma el contexto principal
    context = {
        "data": data,
        "presion_estatica": round(presion_estatica, 1),
        "presion_dinamica": round(presion_dinamica, 1),
        "perdida_de_choque": round(perdida_total, 0),
        "perdidas_friccionales": round(perdidas_friccionales, 0),
        "variables": variables
    }
    
    # Actualizar el estado final del semáforo usando el último proyecto
    proyecto = get_last_project()
    semaforo.calcular_estado_final(proyecto)
    # Se obtiene el detalle del semáforo y se fusiona en el contexto
    detalle_semaforo = semaforo.detalle
    context = {**context, **detalle_semaforo}
    # Consolidar el diccionario final eliminando claves innecesarias
    detalle_consolidado = merge_detalle_semaforo(context)
    detalle_consolidado['velocidad_sensor'] = semaforo.fan.densidad_aire_sensores
    detalle_consolidado['v5'] = context.get('v5', None)
    detalle_consolidado['v3'] = context.get('v3', None)

    # Guardar en Historial usando el diccionario consolidado
    guardar_historial_detalle(detalle_consolidado)
    return context
