from django.shortcuts import render
import pandas as pd  # Importa pandas
import numpy as np
from django.http import HttpResponse
import requests as rq

from django.conf import settings
import os

def fandesign(request):
   if request.method == 'GET':
      # Obtener el tipo de gráfico seleccionado desde la solicitud
      chart_type = request.GET.get('chart_type')
      # Lógica para diferentes tipos de gráficos
      if chart_type == 'total_pressure':
         csv_file_path = os.path.join(settings.MEDIA_ROOT, 'AXT0800_pt.csv')
         df = pd.read_csv(csv_file_path)
         scatter_data = df[["caudal", "presionTotal"]]
         print(scatter_data)

         #Reemplazar con datos sensor BD
         csv_file_datos = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
         df2 = pd.read_csv(csv_file_datos)
         caudal = df2["q1"]
         presion_total = df2["pt1"]
         # Calcular promedios
         Q_medido = caudal.mean()
         P_medido = presion_total.mean()
         print(Q_medido)
         print(P_medido)

      elif chart_type == 'static_pressure':
         csv_file_path = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
         df = pd.read_csv(csv_file_path)

         scatter_data = df[["caudal", "presion"]]


      elif chart_type == 'power':
         csv_file_path = os.path.join(settings.MEDIA_ROOT, 'AXT0800_pot.csv')
         df = pd.read_csv(csv_file_path)

         scatter_data = df[["caudal", "potencia"]]
      else:
         return render(request, 'fanDesign.html')

      # Convierte los datos a una lista de diccionarios
      scatter_data_list = scatter_data.to_dict(orient='records')

      # Pasa los datos a la plantilla
      context = {'scatter_data': scatter_data_list, 'chart_type': chart_type, 'promedios':[Q_medido,P_medido]}
      return render(request, 'fanDesign.html', context)

   # Si la solicitud no es un POST, simplemente renderiza la página sin datos
   return render(request, 'fanDesign.html')
