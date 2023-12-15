import pandas as pd
from django.conf import settings
import os

# Diccionario que mapea tipo -> columnas 
CHART_MAP = {
   "pt": ["caudal", "presionTotal", "densidad", "rpm"],
   "pot": ["caudal", "potencia", "densidad", "rpm"]
}

def get_fan_data(chart_type):
   # leer csv fan
   csv_fan_path = os.path.join(settings.MEDIA_ROOT, 'AXT0800_'+chart_type+'.csv')
   df_fan = pd.read_csv(csv_fan_path)
   df_fan["densidad"] = df_fan["densidad"].mean()  
   df_fan["rpm"] = df_fan["rpm"].mean()
   columns = CHART_MAP[chart_type]
   df_fan = df_fan[columns]
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
   
# def get_averages(df):
#    # calcular promedios en base a df
#    # return promedios


# def build_context(chart_type):
#    sensor_df = get_sensor_data()  
#    fan_df = get_fan_data()
      
#    averages = get_averages(sensor_df)  
   
#    return {
#         "data": fan_df,
#         "averages": averages
#    }