from django.shortcuts import render
import pandas as pd  # Importa pandas
import numpy as np
from django.http import HttpResponse
import requests as rq

from django.conf import settings
import os

from modules.graphdata import *

def fandesign(request):
   if request.method == 'GET':
      # Obtener el tipo de gráfico seleccionado desde la solicitud
      chart_type = request.GET.get('chart_type')
      # Lógica para diferentes tipos de gráficos
      if chart_type == 'total_pressure':
         ### FAN DATA ###
         df_fan = get_fan_data('pt')
         ### SENSORs DATA ###  #Reemplazar con datos sensor BD
         df_sensor1 = get_sensor_data()
         ### VDF DATA ###
         df_vdf = get_vdf_data()

         Q_medido = df_sensor1["q1"].mean()
         P_medido = df_sensor1["pt1"].mean()
         densidad_sensor1 = df_sensor1["densidad1"].mean()
         rpm_vdf = df_vdf["rpm"].mean()

      elif chart_type == 'static_pressure':
         ### FAN DATA ###
         df_fan = get_fan_data('pt')
         ### SENSORs DATA ###  #Reemplazar con datos sensor BD
         df_sensor1 = get_sensor_data()
         ### VDF DATA ###
         df_vdf = get_vdf_data()

         Q_medido = df_sensor1["q1"].mean()
         P_medido = df_sensor1["pe1"].mean()
         densidad_sensor1 = df_sensor1["densidad1"].mean()
         rpm_vdf = df_vdf["rpm"].mean()

      elif chart_type == 'power':
         ### FAN DATA ###
         df_fan = get_fan_data('pot')
         ### SENSORs DATA ###  #Reemplazar con datos sensor BD
         df_sensor1 = get_sensor_data()
         ### VDF DATA ###
         df_vdf = get_vdf_data()

         Q_medido = df_sensor1["q1"].mean()
         P_medido = df_vdf["potencia"].mean()
         densidad_sensor1 = df_sensor1["densidad1"].mean()
         rpm_vdf = df_vdf["rpm"].mean()
      else:
         return render(request, 'fanDesign.html')

      # Convierte los datos a una lista de diccionarios
      scatter_data_fan_list = df_fan.to_dict(orient='records')

      # Pasa los datos a la plantilla
      context = {'scatter_data': scatter_data_fan_list, 'chart_type': chart_type, 'promedios':[Q_medido,P_medido]}
      return render(request, 'fanDesign.html', context)

   # Si la solicitud no es un POST, simplemente renderiza la página sin datos
   return render(request, 'fanDesign.html')
