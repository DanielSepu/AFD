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
      print(request.GET)
      section = request.GET.get('section')
      # Lógica para diferentes tipos de gráficos
      context  = { 
         'total_pressure':[],
         'static_preassure':[],
         'power':[],
         'section': section
      }
      if section == 'current_Operation':
         context = { 
            'total_pressure': df[["caudal", "presionTotal"]].to_dict(orient='records') ,
            'static_pressure': df[["caudal", "presion"]].to_dict(orient='records'),
            'power': df[["caudal", "potencia"]].to_dict(orient='records'),
            'section': section
         }  
      elif section == 'last_Measurement':
         context = { 
            'total_pressure': df[["caudal", "presionTotal"]].to_dict(orient='records') ,
            'static_pressure': df[["caudal", "presion"]].to_dict(orient='records'),
            'power': df[["caudal", "potencia"]].to_dict(orient='records'),
            'section': section
         }  
      elif section == 'average_Curve':
         context = { 
            'total_pressure': df[["caudal", "presionTotal"]].to_dict(orient='records') ,
            'static_pressure': df[["caudal", "presion"]].to_dict(orient='records'),
            'power': df[["caudal", "potencia"]].to_dict(orient='records'),
            'section': section
         }  
      print(context)
      return render(request, 'fanReal.html', context)

   # Si la solicitud no es un POST, simplemente renderiza la página sin datos
   return render(request, 'fanReal.html')