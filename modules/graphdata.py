import pandas as pd
from django.conf import settings
import os

# Diccionario que mapea tipo -> columnas 
CHART_MAP = {
   "pt": ["caudal", "presionTotal", "densidad", "rpm"],
   "pot": ["caudal", "potencia", "densidad", "rpm"]
}

def  get_fan_data(proyect, chart_type):
   # leer csv fan
   #csv_fan_path = os.path.join(settings.MEDIA_ROOT, 'AXT0800_'+chart_type+'.csv')
   #df_fan = pd.read_csv(csv_fan_path)
   
   if proyect != None:
      print(dict(proyect.curva_diseno.datos_curva))
      df_fan = pd.DataFrame(dict(proyect.curva_diseno.datos_curva))
   else:
      raise ValueError("No hay proyecto asignado")
   #  df_fan["rpm"] = df_fan["rpm"].mean()

   return df_fan 

def get_sensor_data():
   # leer csv sensor
   csv_sensor1_path = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
   df_sensor1 = pd.read_csv(csv_sensor1_path)
   return df_sensor1

def get_vdf_data():
   # leer csv sensor
   csv_vdf_path = os.path.join(settings.MEDIA_ROOT, 'datosVDF.csv')
   df_vdf = pd.read_csv(csv_vdf_path)
   return df_vdf

### Ajustes ###
def rpm_adjust_caudal(caudal, rpm_fan, rpm_vdf):
   # calcular promedios en base a df
   df_adjust = pd.DataFrame()
   df_adjust = caudal * (rpm_vdf/rpm_fan)
   return df_adjust

def rpm_adjust_pt(presion, rpm_fan, rpm_vdf):
   # calcular promedios en base a df
   df_adjust = pd.DataFrame()
   df_adjust = presion * (rpm_vdf/rpm_fan)**2
   
   return df_adjust


def rpm_adjust_power(potencia, rpm_fan, rpm_vdf):
   # calcular promedios en base a df
   df_adjust = pd.DataFrame()
   df_adjust = potencia * (rpm_vdf/rpm_fan)**3
   return df_adjust

def dens_adjust_pt(pt_rpm, densidad_fan, densidad_sensor1):
   # calcular promedios en base a df
   df_adjust = pd.DataFrame()
   df_adjust = pt_rpm * (densidad_sensor1/densidad_fan)
   return df_adjust

def dens_adjust_power(power_rpm, densidad_fan, densidad_sensor1):
   # calcular promedios en base a df
   df_adjust = pd.DataFrame()
   df_adjust = power_rpm * (densidad_sensor1/densidad_fan)
   return df_adjust

def calculate_presion_estatica(presion, caudal, area_difusor, mid_densidad):
   #print(f"presion: {presion} caudal: {caudal} area_difusor: {area_difusor}")
   presion_estatica = pd.DataFrame()
   presion_estatica = presion - mid_densidad *(caudal/area_difusor)**2
   return presion_estatica
# def build_context(chart_type):
#    sensor_df = get_sensor_data()  
#    fan_df = get_fan_data()
      
#    averages = get_averages(sensor_df)  
   
#    return {
#         "data": fan_df,
#         "averages": averages
#    }