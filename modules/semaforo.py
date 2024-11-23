from math import atan, sqrt
import math

import pandas as pd
from applications.fandesign.mixins import presion_total
from applications.getdata.models import SensorsData, VdfData
from modules.queries import get_10min_sensor_data, get_10min_vdf_data
from IPython.display import display, Markdown
from django.contrib import messages

from IPython.display import display, HTML

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
    def __init__(self, request):
        self.estado = 'verde'
        self.sensorData = None
        self.vdfData = None
        self.project = None
        self.request = request
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
        self.detalle["sensor"] = dataframe_sensor.to_html(index=False)
        self.project = project

        # Mostrar vdf
        numeric_vdf_data = self.vdfData.select_dtypes(include='number')
        dataframe_vdfDatatranspose = numeric_vdf_data.mean().round(2).to_frame().transpose()
        dataframe_vdfDatatranspose = dataframe_vdfDatatranspose.iloc[0]
        dataframe_vdfDatatranspose = dataframe_vdfDatatranspose.iloc[1:]

        dataframe_transpose_vdf = numeric_vdf_data.mean().round(2)
        dataframe_vdf = pd.DataFrame([dataframe_transpose_vdf])
        self.detalle["vdf"] = dataframe_vdf.to_html(index=False)

    def calculate_tbh(self, tbs, hr):
        # tbh1 =E13*ATAN(0.151977*  SQRT(E8+8.313659))+     ATAN(E13+E8)-   ATAN(E8-1.6763)+    0.00391838*     POWER(E8,1.5)*ATAN(0.023101*E8)-4.686
        #  = E16 *ATAN(0.151977* SQRT(E17+8.313659))+    ATAN(E16+E17)-  ATAN(E17-1.6763)+   0.00391838*     POWER(E17,1.5)*ATAN(0.023101*E17)-4.686
        
        return tbs * atan(0.151977 * sqrt(hr + 8.313659)) + atan(tbs + hr) - atan(hr - 1.6763) + 0.00391838 * pow(hr, 1.5) * atan(0.023101 * hr) - 4.686035

    def calcular_area_ducto(self):
        area_ducto = None
        if self.project.ducto.t_ducto == "circular":
            area_ducto = 3.14159 * self.project.ducto.diametro**2

        if self.project.ducto.t_ducto == "ovalado":
            area_ducto = self.project.ducto.area
        
        if area_ducto == None:
            #raise ValueError("NO hemos calculado el area del ducto correctamente.")
            messages.error(self.request, "Error algunos valores para calcular el area del ducto no se han especificado, verifique: tipo ducto: {self.project.ducto.t_ducto} y sus valores")
        return area_ducto

    def calcular_velocidad_sensor(self, tbs, hr, P, pt, ps, tipo):

        # set de operaciones
        Tbh2 = self.calculate_tbh(tbs, hr)
        # =616.6*   EXP(17.27*E13/(237.3+E13))

        esd =  616.6*math.exp((17.27 * tbs) / (237.3 + tbs)) # Calcula la presión de vapor del agua a temperatura seca
        # =616.6    *   EXP(17.27*J6/(237.3+J6))
        esw = 616.6*math.exp((17.27 * Tbh2) / (237.3 + Tbh2)) # Calcula la presión de vapor del agua a temperatura húmeda
        Xs = 0.622*esw/(P-esw) # humedad absoluta en kg vapor de agua por kg aire seco
        Lw = (2502.5-2.386*Tbh2)*1000 # J/kg 
        S = Lw*Xs + 1005*Tbh2; # J/kg
        X = (S-1005*tbs)/(Lw+1884*(tbs-Tbh2))
        e = P*X/(0.622+X); #  Pa 


        # crear un diccionario de los valores, para imprimir en la tabla dinamica
        values_dic = {
            'tbh2': Tbh2,
            'esd': esd,
            'esw': esw,
            'Xs': Xs,
            'Lw': Lw,
            'S': S,
            'X': X,
            'e': e
        }

        titulo = "Variables de entrada"
        # mostrar_reporte(titulo, Tbh2, esd, esw, Xs, Lw, S, X, e)

        densidad_aire_frente = (P-e)/(287.04*(tbs+273.15)); #  Kg aire seco/m3

        # =SQRT(2*(E5-E6)/E22)
        try:
            velocidad_sensor = sqrt(2*(pt-ps)/densidad_aire_frente) # Densidad aire en la frente)   2 decimales >>> velocidad aire sensor frente
        except ValueError as e:
            messages.error(self.request, f"Alerta un numero intenta realizar un calculo con un valor bajo cero: {e}")
            velocidad_sensor = 0
        values_dic = {
            'densidad_aire_frente': densidad_aire_frente,
            'pt': pt,
            'ps': ps,
            'velocidad_sensor': velocidad_sensor
        }
        titulo = "Resultados"
        return velocidad_sensor

    def calculate_Q2(self):
        """
            
            Crear variable Q2) Caudal sensor 2 (Q2) m3/s = velocidad sensor 2 (m/s)*Área ducto (m2)
        Returns:
            _type_: _description_
        """
        if self.Q2 != None:
            return self.Q2

        # calcular densidad aire en la frente
        HRf  = self.sensorData["q2"].mean()
        # temperatura bulbo seco
        Tbs2 = self.sensorData["lc"].mean()
        # presion barometrica en la frente
        P2  = self.sensorData["densidad2"].mean()
        # definir variables
        pt2 = self.sensorData["pt2"].mean()

        ps2 = self.sensorData["ps2"].mean()
        
        velocidad_sensor_2 = self.calcular_velocidad_sensor(Tbs2, HRf, P2, pt2, ps2, "solicitado desde Q2" )
        area_ducto = self.calcular_area_ducto()
        # = J22  * E24
        Q2 = velocidad_sensor_2 * area_ducto  #  caudal sensor 2 = (m/s)/(m2)
        
        # asignar al entorno global
        self.Q2 = Q2
        return Q2

    def calculate_Q1(self):
        #definir las variables de los sensores y el proyecto
        # ---> sensores
        # definir variables
        
        # comprobar si ya fue calculada
        if self.Q1 != None:
            return self.Q1
        

        pt1 = self.sensorData["pt1"].mean()
        ps1 = self.sensorData["ps1"].mean()
        tbs = self.sensorData["tbs"].mean() # humedad relativa
        hr = self.sensorData["hr"].mean() # temperatura bulbo seco
        P1 = self.sensorData["densidad1"].mean()  #  Presión barométrica ventilador
        tbs1 = self.sensorData["lc"].mean() # 
        velocidad_sensor_1 = self.calcular_velocidad_sensor(tbs, hr, P1, pt1, ps1, "solicitado desde Q1" )
        # velocidad_sensor_1 = self.calcular_velocidad_sensor1()   # 2 decimales

        area_ducto = self.calcular_area_ducto()
        Q1  = velocidad_sensor_1 *area_ducto #  m3/s = (m2)*(m/s).  (Crear variable Q1) caudal_ventilador_2
        # asignar a las variables del entorno global 
        self.Q1 = Q1  # guardar el resultado en el entorno global para usarlo en otros metodos
        return Q1

    def calcular_semaforo_v1(self, Qf):
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
        raise Exception("No se logro calcular un valor para el semaforo")
    

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
        lf = self.project.lf

        Qf = Q2 - Lc*0.5*pt2*(lf/100000)
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
        return Qf
    
    def calculate_tbh(self, tbs, hr):
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
            "75-25": [30.6, 28, 25.9],
            "50-50": [31.4, 29.4, 27.9],
            "25-75%": [32.2, 31.1, 30]
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
            color = "rojo"
            return nivel_carga, minimo, maximo, "rojo"
        
        if tgbh > maximo:
            color = "rojo"
            return nivel_carga, minimo, maximo, "rojo"
        color = "verde"
        return nivel_carga, minimo, maximo,"verde"
    
    def tgbh_v3(self):
        """
            TGBH = 0.7*t° bulbo humedo + 0.3*t°bulbo seco
            tbh : temperatura bulbo humedo 
            tbs : temperatura bulbo seco
        Returns:
            TGBH (float): resultado de la formulat TBGH
        """
        formula = f'''tgbh = (0.7 * tbh + (0.3 * tbs'''
        tbh = self.sensorData["tbh"].mean()
        tbs = self.sensorData["tbs"].mean()
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

        Lc = 3*(Q1-Q2)*(pt1-pt2)/(2*L*(pow(pt1,1.5)-pow(pt2,1.5)))*100*pow(1000,0.5)
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
        pt2 = self.sensorData["pt2"].mean()
        
        presion_total_df =  presion_total(self.project, self.vdfData, self.sensorData)
        # obtener el valor maximo del dataframe que contiene la curva ajustada
        presion_maxima_curvaAjustada = presion_total_df['presion'].max()
        fila = presion_total_df.loc[presion_total_df['presion'] == presion_maxima_curvaAjustada ]
    

        
        stall = pt2 / presion_maxima_curvaAjustada * 100
        color = self.calcular_semaforo_v5(stall)
        self.detalle['v5'] = {
            'pt2': round(pt2,3),
            'presion_maxima': round(presion_maxima_curvaAjustada,3),
            'stall': round(stall,3),
            'color': self.calcular_semaforo_v5(stall),
            'formula': "stall = pt2 / presion_maxima_curvaAjustada * 100"
        }
        self.detalle["colores"].append(color)
        return stall


    def calcular_semaforo_v6(self, porcentaje):
        if porcentaje < 0.05:
            return "verde"
        
        if porcentaje > 0.05 and porcentaje < 0.10:
            return "amarillo"
        
        if porcentaje > 0.10:
            return "rojo"
    

    def fugas_v6(self):
        # objetivo 30 minutos 
        media_hora_seg = 30*60

        presion_total_ventilador = SensorsData.objects.all().last() 
        fecha_hora = presion_total_ventilador.ts 

        anterior = SensorsData.objects.exclude(id=presion_total_ventilador.id).last()
        fecha_hora_anterior = anterior.ts

        diferencia = fecha_hora - fecha_hora_anterior

        segundos_diferencia = diferencia.total_seconds()

        
        if segundos_diferencia > 0:
            unidades_faltantes = (media_hora_seg / segundos_diferencia)
            unidades_faltantes = max(0, unidades_faltantes)
        else:
            unidades_faltantes = float("inf")
        
        ultimos_30mins = SensorsData.objects.all().order_by('-id')[:int(unidades_faltantes)+3]
        primero = ultimos_30mins[0]
        ultimo = ultimos_30mins[len(ultimos_30mins) - 1]

        presion_actual = ultimo.pt1 
        presion_hace30m = primero.pt1
        porcentaje = 1 - (presion_hace30m/presion_actual)
        formula = "porcentaje = 1 - (presion_hace30m/presion_actual)"
        color = self.calcular_semaforo_v6(porcentaje)
        self.detalle["colores"].append(color)
        self.detalle['v6'] = {
            "intervalo en segundos": round(segundos_diferencia, 3),
            "presion actual": round(presion_actual, 3),
            "presion hace30m": round(presion_hace30m, 3),
            "porcentaje": round(porcentaje, 3),
            "formula": formula,
            "color": color
        }
        return color

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
        self.caudal_en_la_frente_v1()
        self.velocidad_del_aire_v2()
        self.tgbh_v3()
        self.leakage_coefficient_v4()
        self.punto_de_stall_v5()
        self.fugas_v6()
        self.potencia_v7()
        color = ""
        if "rojo" in self.detalle['colores']:
            color = "rojo"

        elif not "rojo" in self.detalle['colores'] and "amarillo" in self.detalle['colores']:
            color = "amarillo"
        else:
            color = "verde"
        self.detalle["color"] =color

    

    def calculate_k(self):

        mostrar_inicio_formulas_principales("Calculando el valor de K","K (factor de fricción ducto) kg/m3 = (ps1-ps2)*(pow(Área ducto,3))/(Q1*Q2*Perímetro ducto*L)")
        ps1 = self.sensorData['ps1'].mean()
        ps2 = self.sensorData['ps2'].mean()
        area_ducto = self.calcular_area_ducto()
        Q1 = self.calculate_Q1()
        Q2 = self.calculate_Q2()
        #perimetro_ducto = self.

        separador()
        return 0
