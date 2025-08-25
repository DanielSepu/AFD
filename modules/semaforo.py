from datetime import timedelta
from math import atan, sqrt
import math
import traceback

import pandas as pd
import requests
from django.core.exceptions import ObjectDoesNotExist
from applications.settings.models import FugasConfig, SemaforoEstado
from applications.fandesign.mixins import presion_total
from applications.fandesign.utils import calcular_la_curva_total, calcular_la_presion_maxima
from applications.getdata.models import SensorsData, VdfData
from modules.queries import get_10min_sensor_data, get_10min_vdf_data
from django.db.models import Max
from core.logger_config import logger_AFD
from django.db.models import F, ExpressionWrapper, DurationField
from django.utils import timezone



def mostrar_inicio_formulas_principales(str, description):
    display(HTML(f"""
    <hr>
            <h1>{str}</h2>
            <small>{description}</small>
            <br>

    """))
def mostrar_inicio_formula(str, descripcion=None):
    display(HTML(f"""
    <hr>
            <h2>{str}</h2>
            <small>{descripcion}</small>

"""))
def mostrar_inicio_subformula(str, descripcion=None):
    display(HTML(f"""
    <hr>
            <h3>{str}</h3>
            <small>{descripcion}</small>

"""))
def mostrar_semaforo(color):
    # Mapea el color de la luz a estilos de colores
    colores = {
        "rojo": {"rojo": "red", "amarillo": "gray", "verde": "gray"},
        "amarillo": {"rojo": "gray", "amarillo": "yellow", "verde": "gray"},
        "verde": {"rojo": "gray", "amarillo": "gray", "verde": "green"}
    }
    
    # Establece el color de cada luz
    luces = colores.get(color.lower(), {"rojo": "gray", "amarillo": "gray", "verde": "gray"})
    
    # Genera el HTML con el semáforo y el color de luz seleccionado
    display(HTML(f"""
    <div style="border: 2px solid #333; border-radius: 10px; width: 50px; padding: 10px; text-align: center; background: #444;">
        <div style="width: 30px; height: 30px; background-color: {luces['rojo']}; border-radius: 50%; margin: 5px auto;"></div>
        <div style="width: 30px; height: 30px; background-color: {luces['amarillo']}; border-radius: 50%; margin: 5px auto;"></div>
        <div style="width: 30px; height: 30px; background-color: {luces['verde']}; border-radius: 50%; margin: 5px auto;"></div>
    </div>
    """))
    
def separador():
    display(HTML("<hr>"))

def mostrar_en_tabla_dinamica(titulo, values_dic):
    # Extraer los encabezados y valores de los datos del diccionario
    headers = list(values_dic.keys())
    values = list(values_dic.values())
    
    # Generar la tabla dinámica con los encabezados y valores del diccionario
    display(HTML(f"""
    <h3>{titulo}</h3>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            {''.join(f"<th>{header}</th>" for header in headers)}
        </tr>
        <tr>
            {''.join(f"<td>{value}</td>" for value in values)}
        </tr>
    </table>
    """))

def mostrar_resultado(resultado ):
    display(HTML(f"""
    <fieldset border="1" cellpadding="5" cellspacing="0">
            <legend>Resultado</legend>
            <p>{str(resultado)}</p>
    </fieldset>
    
    """))

def mostrar_formula(str):
    display(HTML(f"""
    <h3>{str}</h3>
    """))


class Semaforo:
    """
    Clase que representa un semaforo de control de estado de la ventilacion del sistema de ventilacion de la mina,
    el semaforo tiene  7 variables para medir, que pueden retornar verde, rojo, o amarillo cada una de sus funciones, a partir
    de la sumatoria de cada resultado de las 7 variables se pondera el estado final.
    """
    def __init__(self, fan):
        self.estado = 'verde'
        self.sensorData = None
        self.fan = fan
        self.vdfData = None
        self.project = None
        self.Q1 = None 
        self.Q2 = None 
        self.detalle = {
            "colores": [],
        }

    
    def encender(self, project):
        self.vdfData = get_10min_vdf_data()
        self.sensorData = get_10min_sensor_data()

        # Filtrar solo columnas numéricas antes de calcular la media
        numeric_sensor_data = self.sensorData.select_dtypes(include='number')
        dataframe_transpose = numeric_sensor_data.mean().round(2)
        dataframe_sensor = pd.DataFrame([dataframe_transpose])

        dict_sensor = dict(dataframe_sensor.iloc[0].to_dict())
        # Excluir la columna 'id' y todas las columnas desde 'k' en adelante
        
        # Paso 1: obtener todas las columnas
        todas_las_columnas = list(dataframe_sensor.columns)

        # Paso 2: encontrar el índice de la columna 'k'
        # indice_k = todas_las_columnas.index('k')

        # Paso 3: conservar solo las columnas antes de 'k' y que no sean 'id'
        #columnas_filtradas = [col for col in todas_las_columnas[:indice_k] if col != 'id']

        # Paso 4: aplicar filtro y guardar HTML
        self.detalle["sensor"] = dataframe_sensor[todas_las_columnas].to_html(index=False)

        self.project = project

        # Mostrar vdf
        numeric_vdf_data = self.vdfData.select_dtypes(include='number')
        dataframe_vdfDatatranspose = numeric_vdf_data.mean().round(2).to_frame().transpose()
        dataframe_vdfDatatranspose = dataframe_vdfDatatranspose.iloc[0]
        dataframe_vdfDatatranspose = dataframe_vdfDatatranspose.iloc[1:]

        dataframe_transpose_vdf = numeric_vdf_data.mean().round(2)
        dataframe_vdf = pd.DataFrame([dataframe_transpose_vdf])
        self.detalle["vdf"] = dataframe_vdf.to_html(index=False)

    def calcular_area_ducto(self):
        
        area_ducto = None
        try:
            if self.project.ducto.t_ducto == "circular":
                area_ducto = 3.14159 * self.project.ducto.diametro**2

            if self.project.ducto.t_ducto == "ovalado":
                area_ducto = self.project.ducto.area
            
            if area_ducto == None:
                pass
                # messages.warning(self.request, f"Error algunos valores para calcular el area del ducto no se han especificado, verifique: tipo ducto: {self.project.ducto.t_ducto} y sus valores")
            area_ducto = area_ducto/4000000 
        except Exception as e:
            if self.project.ducto.t_ducto == "circular":
                raise Exception(f"Los valores actuales no son adecuados para calcular el ducto circular")

            if self.project.ducto.t_ducto == "ovalado":
                raise Exception(f"Los valores actuales no son adecuados para calcular el ducto circular")
        return area_ducto

    def calculate_Q2(self):
        """
            Crear variable Q2) Caudal sensor 2 (Q2) m3/s = velocidad sensor 2 (m/s)*Área ducto (m2)
        Returns:
            _type_: _description_
        """
        if self.Q2 != None:
            return self.Q2

        
        # = J22  * E24
        try:
            velocidad_sensor_2 = self.fan.velocidad_aire_sensores['sensor2']
            area_ducto = self.calcular_area_ducto()
            Q2 = velocidad_sensor_2 * area_ducto  #  caudal sensor 2 = (m/s)/(m2)
        except TypeError as e: #
            raise Exception(f"error en calculate_Q2: {e} {self.calcular_area_ducto()}")
            # messages.warning(self.request, f"error al calcuar Q2: los valores no se pueden procesar: {e}, verifique los errores de: q2, lc, densidad2, pt2, ps2, area_ducto, ")
            Q2 = 0
        except KeyError as e:
            Q2 = 0
            raise Exception(f"error en calculate_Q2: {e}")
            # messages.warning(self.request, f"La base de datos del sensor aun no recibe datos")
            # calcular densidad aire en la frente
            HRf  = 0
            # temperatura bulbo seco
            Tbs2 = 0
            # presion barometrica en la frente
            P2  = 0
            # definir variables
            pt2 = 0

            ps2 = 0
        # asignar al entorno global
        self.Q2 = Q2
        return Q2

    def calculate_Q1(self):
        # calcular el caudal del ventilador
        
        # comprobar si ya fue calculada
        if self.Q1 != None:
            return self.Q1   
        try:
            velocidad_sensor_1 = self.fan.velocidad_aire_sensores['sensor1']
            area_ducto = self.calcular_area_ducto()
            Q1  = velocidad_sensor_1 *area_ducto #  m3/s = (m2)*(m/s).  (Crear variable Q1) caudal_ventilador_2
        except TypeError as e: #
            # messages.warning(self.request, f"error al calcuar Q1: los valores no se pueden procesar: {e}, verifique los errores de: q2, lc, densidad2, pt2, ps2, area_ducto, ")
            Q1 = 0
        except KeyError as e:
            print(f"error en calculate_Q1: {e}")

            velocidad_sensor_1 = 0
        # asignar a las variables del entorno global 
        self.Q1 = Q1  # guardar el resultado en el entorno global para usarlo en otros metodos
        return Q1

    def calcular_semaforo_v1(self, Qf):
        Qf=int(Qf)
        equipamiento_diesel = self.project.equipamientos.all()
        
        caudal_requerido = 0 
        for equipo in equipamiento_diesel:
            caudal_requerido += equipo.qr_calculado
        dic_ = {
            "Qf": Qf,
            "caudal requerido": caudal_requerido
        }

        if caudal_requerido < Qf:
            color = "rojo"
            return  color
        if caudal_requerido > Qf :
            color = "verde"
            return color
        raise Exception(f"No se logro calcular un valor para el semaforo valor: {Qf}")
    
    
    def calcular_qf(self, Q2, Lc, pt2, lf):
        return Q2 - Lc*0.5*pt2*(lf/100000)
        
        
    def caudal_en_la_frente_v1(self):
        """
        Calcula el caudal en la frente del ventilador
        formula: Qf (caudal de la frente) m3/s = Qf = Q2 - Lc*0.5*pt2*Lf /(100000);

        Returns:
            float: resultado de la aplicacion de la formula
        """
        # definir las variables requeridas

        
        Q2 = self.calculate_Q2()
        Lc = self.leakage_coefficient_v4()
        pt2 = self.sensorData["pt2"].mean()
        lf = self.project.ducto.dS2_F

        Qf = self.calcular_qf( Q2, Lc, pt2, lf)
        formula = "Qf = Q2 - Lc*0.5*pt2*(lf/100000)"

        values_dic = {
            'Q2 calculada': Q2,
            'Lc calculada': Lc,
            'pt2 ': pt2,
            'lf': lf,
        }

        color = self.calcular_semaforo_v1(Qf)
        self.detalle["colores"].append(color)

        self.detalle["v1"] = {
            'Q2': round(Q2, 3),
            'Qf': round(Qf, 3),
            'lc': round(Lc, 3),
            'pt2': round(pt2, 3),
            'lf': round(lf, 3),
            'formula': formula,
            'color': color
        }
        # logger_AFD.debug(f"---> caudal: Lc: {Lc} Qf: {Qf} Q2: {Q2} pt2: {pt2} lf: {lf}")
        return Qf
    
    def calculate_tbh(self, tbs, hr):
        # tbh1 =E13*ATAN(0.151977*  SQRT(E8+8.313659))+     ATAN(E13+E8)-   ATAN(E8-1.6763)+    0.00391838*     POWER(E8,1.5)*ATAN(0.023101*E8)-4.686
        #  = E16 *ATAN(0.151977* SQRT(E17+8.313659))+    ATAN(E16+E17)-  ATAN(E17-1.6763)+   0.00391838*     POWER(E17,1.5)*ATAN(0.023101*E17)-4.686

        return tbs * atan(0.151977 * sqrt(hr + 8.313659)) + atan(tbs + hr) - atan(hr - 1.6763) + 0.00391838 * pow(hr, 1.5) * atan(0.023101 * hr) - 4.686035

    def calcular_semaforo_v2(self, velocidad_del_aire):
        if velocidad_del_aire > 0.25 and velocidad_del_aire < 2.5:
            color = "verde"
            return color
        color = "rojo"
        return color

    def velocidad_del_aire_v2(self):
        """
        se encarga de calcular la densidad del aire en la frente del ventilador

        formula: Densidad aire en la frente = (P2-e)/(287.04*(Tbs2+273.15)); // Kg aire seco/m3

        Returns:
            float: densidad del aire en la frente
        """
        #definir las variables de los sensores y el proyecto
        # ---> sensores

        caudal_ventilador = self.caudal_en_la_frente_v1()
        Q1 = self.calculate_Q1()
        Area_galeria = self.project.area_galeria 
        velocidad_del_aire = Q1/Area_galeria
        dict_result  = {
            'Q1': Q1,
            'Area_galeria': Area_galeria
        }
        formula = 'velocidad_del_aire = Q1/Area_galeria'
        color = self.calcular_semaforo_v2(velocidad_del_aire)
        self.detalle['v2'] = {
            'Q1': round(Q1, 3),
            'Area_galeria': round(Area_galeria, 3),
            'velocidad_del_aire': round(velocidad_del_aire, 3),
            'color': color,
            'formula': formula
        }
        self.detalle["colores"].append(color)
        
        return velocidad_del_aire
    
    def calcular_estado_v3(self, tgbh):
        # Crear el DataFrame
        data = {
            "trabajo continuo": [30, 26.7, 25],
            "75-25":            [30.6, 28, 25.9],
            "50-50":            [31.4, 29.4, 27.9],
            "25-75%":           [32.2, 31.1, 30]
        }

        # Definir los índices
        indices = ["liviana", "moderada", "pesada"]

        # Crear el DataFrame con el índice especificado
        df = pd.DataFrame(data, index=indices)
        nivel_carga = self.project.nivel_carga
        fila = df.loc[nivel_carga]
        minimo = fila.iloc[0]
        maximo = fila.iloc[-1]
        if tgbh < minimo :
            return nivel_carga, minimo, maximo, "verde"
        
        if tgbh > maximo:
            return nivel_carga, minimo, maximo, "rojo"
        return nivel_carga, minimo, maximo,"amarillo"
    
    def tgbh_v3(self):
        """
            TGBH = 0.7*t° bulbo humedo + 0.3*t°bulbo seco
            tbh : temperatura bulbo humedo 
            tbs : temperatura bulbo seco
        Returns:
            TGBH (float): resultado de la formulat TBGH
        """
        formula = f'''tgbh = (0.7 * tbh + (0.3 * tbs'''
        tbs = self.sensorData["Tbs1"].mean()
        Tbs2  = self.sensorData["Tbs2"].mean()
        humedad_relativa_s1 = self.sensorData['HRs1'].mean()
        tbh = self.calculate_tbh(Tbs2, humedad_relativa_s1)
        
        tgbh = (0.7 * tbh) + (0.3 * tbs)

        nivel_carga, min, max, color = self.calcular_estado_v3(tgbh)
        
        self.detalle['v3'] = {
            'tbh': round(tbh, 3),
            'tbs': round(tbs, 3),
            'tgbh': round(tgbh, 3),
            'color': color,
            'min': min,
            'max': max,
            'nivel_carga': nivel_carga,
            'formula': formula,
        }
        
        
        self.detalle["colores"].append(color)
        return tgbh
    
    def calcular_semaforo_v4(self, lc):
        if lc < 0.5:
            return "verde"
        
        if lc > 0.5 and lc < 1:

            return "amarillo"
        
        if lc > 1:
            return "rojo"
        return 0
    

    def leakage_coefficient_v4(self):
        Q1 = self.calculate_Q1()
        Q2 = self.calculate_Q2()

        pt1 = self.sensorData["pt1"].mean() 
        pt2 = self.sensorData["pt2"].mean()
        
        L = self.project.dis_e_sens
        Lc = (3  * (Q1-Q2)  * (pt1-pt2)    /   (2    *   L  * (pow(pt1,1.5)    -   pow(pt2,1.5))   )) * 100    * pow(1000,0.5)
        formula = "Lc = 3 * (Q1-Q2) * (pt1-pt2) / ( 2 * L *(pow(pt1,1.5)  - pow(pt2,1.5) )) * 100 * pow(1000,0.5)"
        color = self.calcular_semaforo_v4(Lc)
        self.detalle['v4'] = {
            'Q1': round(Q1, 3),
            'Q2': round(Q2,3),
            'pt1': round(pt1,3),
            'pt2': round(pt2,3),
            'L': round(L,3),
            'Lc': round(Lc, 3),
            'color': color,
            'formula': formula,
        }
        self.detalle["colores"].append(color)
        return Lc 

    def calcular_semaforo_v5(self, stall):
        if stall < .90:
            return "verde"
        
        return "rojo"
    

    def punto_de_stall_v5(self):
        pt1 = self.sensorData["pt1"].mean()
        presion_total_df =  presion_total(self.project, self.vdfData, self.sensorData)
        # obtener el valor maximo del dataframe que contiene la curva ajustada
        presion_maxima_curvaAjustada = presion_total_df['presion'].max()
        fila = presion_total_df.loc[presion_total_df['presion'] == presion_maxima_curvaAjustada ]
        stall = pt1 / presion_maxima_curvaAjustada * 100
        
        df_fan = pd.DataFrame(data=dict(self.project.curva_diseno.datos_curva), dtype=float)
        rpm_del_proyecto = self.project.curva_diseno.rpm
        densidad1 = self.project.curva_diseno.densidad
        rpm_model = self.vdfData['rpm'].mean()
        
        # calculando la densidad
        densidad2 = self.fan.densidad_del_aire_s1()
        df_total_pressure  = calcular_la_curva_total(df_fan, rpm_model, rpm_del_proyecto, densidad2, densidad1 )
        indice_max = df_total_pressure["presion"].idxmax()
        latest_record_sensors = SensorsData.objects.using('sensorDB').aggregate(Max('id'))
        max_id_sensors = latest_record_sensors['id__max']
        item_sensors = SensorsData.objects.using('sensorDB').get(id=max_id_sensors)
        
        presion_maxima_curvaAjustada = df_total_pressure["presion"].max()
        presion_maxima = calcular_la_presion_maxima(item_sensors, df_total_pressure, indice_max) 
        color = self.calcular_semaforo_v5(presion_maxima)
        logger_AFD.info(f"punto de stall: {presion_maxima}")
        self.detalle['v5'] = {
            'pt2': round(pt1,3),
            'presion_maxima': round(presion_maxima_curvaAjustada,3),
            'stall': f"{round(stall,3)} %",
            'color': self.calcular_semaforo_v5(stall),
            'formula': "stall = pt1 / presion_maxima_curvaAjustada * 100"
        }
        self.detalle["colores"].append(color)
        return presion_maxima

    def calcular_semaforo_v6(self, porcentaje):
        config = FugasConfig.objects.first()
        semaforo = SemaforoEstado.objects.first()
        
        if not config or not semaforo:
            logger_AFD.warning("Configuración de fugas o semáforo no disponible.")
            mensaje ="ALERTA DE SISTEMA: No podemos calcular el color del semaforo en las fugas, falta la configuración del promedio y los rangos de tolerancia de las fugas"
            return mensaje, "amarillo"

        

        # Determinar color según tolerancias dinámicas
        tolerancia_verde = config.tolerancia_minima/100
        tolerancia_amarillo = config.tolerancia_maxima/100

        if porcentaje <= tolerancia_verde:
            mensaje = f"El porcentaje de caída ({round(porcentaje*100, 2)}%) se encuentra dentro del rango permitido ({round(tolerancia_verde*100, 2)}% - {round(tolerancia_amarillo*100, 2)}%)."
            
            return mensaje, "verde"
        elif porcentaje > tolerancia_verde and porcentaje <= tolerancia_amarillo:
            mensaje = f"El porcentaje de caída ({round(porcentaje*100, 2)}%) esta fuera del rango normal ({round(tolerancia_verde*100, 2)}%)."
            
            return mensaje, "amarillo"
        else:
            semaforo.esta_bloqueado = True
            semaforo.motivo_bloqueo = f"Fuga crítica detectada. Caída del {round(porcentaje*100, 2)}%"
            semaforo.color_actual = "rojo"
            semaforo.save()
            mensaje = f"El porcentaje de caída ({round(porcentaje*100, 2)}%) supera el máximo permitido ({round(tolerancia_amarillo*100, 2)}%)."
            return mensaje, "rojo"


    def fugas_v6(self):
        """
        Evalúa posibles fugas de presión en un periodo de 30 minutos.

        La función toma el timestamp más reciente (`ts`) del modelo SensorsData y calcula 
        un rango de 30 minutos hacia atrás. Luego, recupera todos los registros dentro 
        de ese intervalo y calcula la variación porcentual de la presión entre el primer 
        y el último registro.

        Si hay pérdida de presión, se calcula el porcentaje de variación y se evalúa 
        un color de semáforo usando `self.calcular_semaforo_v6`.

        Los resultados se almacenan en `self.detalle['v6']` y el color se devuelve.

        Returns:
            str: Color del semáforo (ej. "verde", "amarillo", "rojo").
        """
        # Paso 1: Obtener el registro más reciente
        message = ""

        try:
            semaforo = SemaforoEstado.objects.latest('id')  # O usa 'fecha' si tienes campo timestamp
        except ObjectDoesNotExist:
            semaforo = None  # No hay registros

        if semaforo and semaforo.esta_bloqueado:
            logger_AFD.warning("Semáforo bloqueado. No se ejecuta análisis.")
            self.detalle['v6'] = {
                "estado": "bloqueado",
                "color": semaforo.color_actual
            }
            message = "El análisis está bloqueado por el semáforo."
            color = "rojo"
        
        
        registro_mas_reciente = SensorsData.objects.using('sensorDB').all().last()
        if not registro_mas_reciente:
            logger_AFD.warning("No hay registros en SensorsData.")
            message ="No hay registros almacenados para el sensor"
            color ="rojo"

        # obtener los promedios de la presion en 5 minutos y 30 minutos
        mean_30m, mean_5m = self.auxiliar_fugas()
        
        
        
        porcentaje = (mean_5m - mean_30m) / mean_30m
        logger_AFD.debug(f"porcentaje: {porcentaje}") 
        formula = "porcentaje = 1 - (presion_hace30m / presion_actual)"
        message, color = self.calcular_semaforo_v6(porcentaje=porcentaje)
        self.detalle.setdefault("colores", []).append(color)

        semaforo.color_actual = color
        semaforo.save()
        # TODO: si el valor del calculo es negativo, se convierte a positivo, si es positivo se ignora
        self.detalle['v6'] = {
            "intervalo en segundos": 30,
            "presion actual": round(mean_5m, 3),
            "presion hace30m": round(mean_30m, 3),
            "porcentaje": f"{int(porcentaje*100)} %",
            "formula": formula,
            "message": message,
            "color": color
        }

        # logger_AFD.debug(f"Resultado fugas_v6: {self.detalle['v6']}")

        return color

    def auxiliar_fugas(self):
        ahora = timezone.now()
        ventana_50m = ahora - timedelta(minutes=50)
        qs = (
            SensorsData.objects
            .using('sensorDB')
            .filter(ts__gte=ventana_50m, ts__lte=ahora)
            .values('ts', 'pt1')
        )
        df = pd.DataFrame.from_records(qs)
        if df.empty:
            # raise ValueError("No se encontraron lecturas en los últimos 50 min")
            pass
        df['ts'] = pd.to_datetime(df['ts'], utc=True)  # asegura zona horaria correcta
        df = df.set_index('ts').sort_index()

        # 1. calcular el promedio de la presion en 5 minutos
        inicio_5m = ahora - timedelta(minutes=5)
        mask_5m = df.index >= inicio_5m
        mean_5m = df.loc[mask_5m, 'pt1'].mean()

        # 2. Promedio de los 30 min entre ‑40 y ‑10 (saltando ‑10 a ‑5)
        inicio_30m = ahora - timedelta(minutes=40)
        fin_30m    = ahora - timedelta(minutes=10)
        mask_30m   = (df.index >= inicio_30m) & (df.index < fin_30m)
        mean_30m   = df.loc[mask_30m, 'pt1'].mean()


        logger_AFD.info(f"Media 5 min  (-5 -> 0):   {mean_5m:.2f} Pa")
        logger_AFD.info(f"Media 30 min (-40 -> -10): {mean_30m:.2f} Pa")
        return mean_30m, mean_5m

    def calcular_semaforo_v7(self, potencia):
        if potencia < 95:
            return "verde"
        
        if potencia > 95 and potencia < 99:
            return "amarillo"
        
        if potencia > 99:
            return "rojo"
        return ""


    def potencia_v7(self):
        power = self.project.ventilador.hp
        vdf_data = VdfData.objects.all().last()
        potencia_consumida = vdf_data.power 

        potencia = (potencia_consumida/power)*100
        formula = "potencia = (potencia_consumida/power)*100"
        color = self.calcular_semaforo_v7(potencia)
        self.detalle["colores"].append(color)
        self.detalle['v7'] = {
            "power": round(power, 3),
            "potencia_consumida": round(potencia_consumida, 3),
            "potencia_porcent": round(potencia, 3),
            "color": color,
            "formula": formula
        }
        return potencia
    
    def calcular_estado_final(self, project):
        self.encender(project)
        errores = []
        self.detalle["errores"] = []

        funciones = [
            self.caudal_en_la_frente_v1,
            self.velocidad_del_aire_v2,
            self.tgbh_v3,
            self.leakage_coefficient_v4,
            self.punto_de_stall_v5,
            self.fugas_v6,
            self.potencia_v7
        ]

        for funcion in funciones:
            try:
                funcion()
            except Exception as e:
                traceback.print_exc()
                error_msg = f"[ERROR] en {funcion.__name__}: {str(e)}"
                print(error_msg)
                errores.append(error_msg)

        # Si hubo errores, forzar estado amarillo y registrarlos
        if errores:
            color = "amarillo"
            self.detalle["errores"].extend(errores)
        elif "rojo" in self.detalle['colores']:
            color = "rojo"
        elif "amarillo" in self.detalle['colores']:
            color = "amarillo"
        else:
            color = "verde"

        self.detalle["color"] = color
        self.limpiar_valores_json(self.detalle)
        # logger_AFD.info(self.detalle)
        self.informar_semaforo_fisico(color)

    def limpiar_valores_json(self, obj):
        if isinstance(obj, dict):
            return {k: self.limpiar_valores_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.limpiar_valores_json(i) for i in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None  # o "NaN", o 0.0, según prefieras
            return round(obj, 3)
        return obj


    def informar_semaforo_fisico(self, color: str):
        """
        Envía un GET a http://127.0.0.1:1880/semaforo?value=<n>
        mapeando color→número: verde→1, amarillo→2, rojo→3.
        """
        # 1. Mapeo color → número
        mapa = {
            'verde': 1,
            'amarillo': 2,
            'rojo': 3
        }
        clave = color.strip().lower()
        if clave not in mapa:
            raise ValueError(f"Color inválido: {color!r}. Usa 'verde', 'amarillo' o 'rojo'.")

        valor = mapa[clave]

        # 2. Construir la URL y parámetros
        url = 'http://127.0.0.1:1880/semaforo'
        params = {'value': valor}

        # 3. Hacer la petición
        #print(requests.get(url, params=params, timeout=10))
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            # Manejo de errores de conexión o HTTP
            print(f"[ERROR] No pude notificar semáforo ({color}→{valor}): {e}")
            return False

        # 4. (Opcional) procesar la respuesta
        # si tu endpoint devuelve JSON:
        # data = resp.json()
        # print("Respuesta del semáforo:", data)

        print(f"[OK] Semáforo '{color}' informado con value={valor}")
        return True
        
        
    def calculate_k(self):

        mostrar_inicio_formulas_principales("Calculando el valor de K","K (factor de fricción ducto) kg/m3 = (pt1-ps2)*(pow(Área ducto,3))/(Q1*Q2*Perímetro ducto*L)")
        pt1 = self.sensorData['pt1'].mean()
        ps2 = self.sensorData['ps2'].mean()
        area_ducto = self.calcular_area_ducto()
        Q1 = self.calculate_Q1()
        Q2 = self.calculate_Q2()
        #perimetro_ducto = self.

        # separador()
        return 0
