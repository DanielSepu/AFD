from django.shortcuts import render
import pandas as pd  # Importa pandas
from django.http import HttpResponse
import requests as rq

from django.conf import settings
import os

from modules.queries import get_sensor_data

def currentstatus2(request):
    if request.method == 'POST':
        dataDB = get_sensor_data()
        # Convertir QuerySet a dataframe
        df = pd.DataFrame(list(dataDB.values())) 
        # Preparar tabla HTML
        table_html = df.to_html(classes='table table-striped')
        context = {'table_html': table_html}
        
        return render(request, 'currentStatus.html', context)
    return render(request, 'currentStatus.html')

def currentstatus(request):
    if request.method == 'POST':
        # dataDB = get_sensor_data()
        # print("DB dataDB")
        # print(dataDB)

        csv_file_path = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
        df = pd.read_csv(csv_file_path)
        table_html = df.to_html(classes='table table-striped')
        
        # Pasa los datos a la plantilla
        context = {'table_html': table_html}
        return render(request, 'currentStatus.html', context)
    
    # Si la solicitud no es un POST, simplemente renderiza la página sin datos
    return render(request, 'currentStatus.html')
