from django.shortcuts import render
import pandas as pd  # Importa pandas
from django.http import HttpResponse
import requests as rq

from django.conf import settings
import os

def getdata(request):
    if request.method == 'POST':
        csv_file_path = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
        df = pd.read_csv(csv_file_path)
        table_html = df.to_html(classes='table table-striped')
        
        # Pasa los datos a la plantilla
        context = {'table_html': table_html}
        return render(request, 'getdata.html', context)

    # Si la solicitud no es un POST, simplemente renderiza la página sin datos
    return render(request, 'getdata.html')



