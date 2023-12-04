from django.shortcuts import render
import pandas as pd  # Importa pandas
from django.http import HttpResponse
import requests as rq

from django.conf import settings
import os

def fanreal(request):
   if request.method == 'GET':
      csv_file_path = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
      df = pd.read_csv(csv_file_path)

      # Obtener el tipo de gráfico seleccionado desde la solicitud
      chart_type = request.GET.get('chart_type')

      # Lógica para diferentes tipos de gráficos
      if chart_type == 'total_pressure':
         scatter_data = df[["caudal", "presionTotal"]]
      elif chart_type == 'static_pressure':
         scatter_data = df[["caudal", "presion"]]
      elif chart_type == 'power':
         scatter_data = df[["caudal", "potencia"]]

      # Convierte los datos a una lista de diccionarios
      scatter_data_list = scatter_data.to_dict(orient='records')

      # Pasa los datos a la plantilla
      context = {'scatter_data': scatter_data_list, 'chart_type': chart_type}
      return render(request, 'fanReal.html', context)

   # Si la solicitud no es un POST, simplemente renderiza la página sin datos
   return render(request, 'fanReal.html')
