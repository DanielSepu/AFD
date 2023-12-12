import pdb
from django.shortcuts import render
import pandas as pd  # Importa pandas
from django.http import HttpResponse
import requests as rq

from django.conf import settings
import os



class DataCurrentStatusView:
    
    def __init__(self):
         
         
        #  Inicializa las propiedades como diccionarios vacíos

        self.general = {'FanPerformance': [], 'FanOperation': []}
        self.total_pressure = {'FanPerformance': [], 'FanOperation': []}
        self.static_pressure = {'FanPerformance': [], 'FanOperation': []}
        self.power = {'FanPerformance': [], 'FanOperation': []}
    
    def add_measurement(self, property_name, fan_type, measurement):

        # Añade una medida a la propiedad correspondiente
        if property_name in ['general', 'total_pressure', 'static_pressure', 'power']:
            if fan_type in ['FanPerformance', 'FanOperation']:
                getattr(self, property_name)[fan_type] = measurement
            else:
                print("Error: Fan type must be 'FanPerformance' or 'FanOperation'")
        else:
            print("Error: Invalid property name")
    
    def to_dict(self):
        # Retorna un diccionario con todas las propiedades
        return {
            'general': self.general,
            'total_pressure': self.total_pressure,
            'static_pressure': self.static_pressure,
            'power': self.power
        }
   

def currentstatus(request):
    
    if request.method == 'GET':
        csv_file_path = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
        df = pd.read_csv(csv_file_path)


        # Ejemplo de uso
        data_view = DataCurrentStatusView()

        # Añadiendo medidas
        data_view.add_measurement('general', 'FanPerformance',  df[["caudal", "presionTotal"]].to_dict(orient='records') )
        data_view.add_measurement('general', 'FanOperation', df[["caudal", "presionTotal"]].to_dict(orient='records') )

        data_view.add_measurement('total_pressure', 'FanPerformance', df[["caudal", "presionTotal"]].to_dict(orient='records'))
        data_view.add_measurement('total_pressure', 'FanOperation',  df[["caudal", "presionTotal"]].to_dict(orient='records') )

        data_view.add_measurement('static_pressure', 'FanPerformance',  df[["caudal", "presion"]].to_dict(orient='records'))
        data_view.add_measurement('static_pressure', 'FanOperation',  df[["caudal", "presion"]].to_dict(orient='records'))

        data_view.add_measurement('power', 'FanPerformance', df[["caudal", "potencia"]].to_dict(orient='records'))
        data_view.add_measurement('power', 'FanOperation',df[["caudal", "potencia"]].to_dict(orient='records'))
        
        
        return render(request, 'currentStatus.html', data_view.to_dict())
    
    # Si la solicitud no es un POST, simplemente renderiza la página sin datos
    return render(request, 'currentStatus.html')



