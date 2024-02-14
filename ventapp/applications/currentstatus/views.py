import pdb
from django.shortcuts import render
import pandas as pd  # Importa pandas
from django.http import JsonResponse
import requests as rq

from django.conf import settings
import os

from yaml import serialize


from applications.getdata.models import SensorsData, VdfData, Ventilador, SensorData, CurvaDiseno
from django.db.models import Max



class DataCurrentStatusView:
    
    def __init__(self):
         
         
        #  Inicializa las propiedades como diccionarios vacíos

        self.general = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
        self.total_pressure = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
        self.static_pressure = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
        self.power = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
    
    def add_measurement(self, property_name, fan_type, status, measurement):

        # Añade una medida a la propiedad correspondiente
        if property_name in ['general', 'total_pressure', 'static_pressure', 'power']:
            if fan_type in ['FanPerformance', 'FanOperation']:
                getattr(self, property_name)[fan_type]['data']= measurement
                getattr(self, property_name)[fan_type]['status'] = status
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
        data_view.add_measurement('general', 'FanPerformance','green',df[["q1", "pt1"]].to_dict(orient='records') )
        data_view.add_measurement('general', 'FanOperation','yellow', df[["q1", "pt1"]].to_dict(orient='records') )

        data_view.add_measurement('total_pressure', 'FanPerformance','red', df[["q1", "pt1"]].to_dict(orient='records'))
        data_view.add_measurement('total_pressure', 'FanOperation', 'yellow',  df[["q1", "pt1"]].to_dict(orient='records') )

        data_view.add_measurement('static_pressure', 'FanPerformance','red',  df[["q1", "pt1"]].to_dict(orient='records'))
        data_view.add_measurement('static_pressure', 'FanOperation','green',  df[["q1", "pt1"]].to_dict(orient='records'))

        data_view.add_measurement('power', 'FanPerformance','red', df[["q1", "pt1"]].to_dict(orient='records'))
        data_view.add_measurement('power', 'FanOperation', 'yellow', df[["q1", "pt1"]].to_dict(orient='records'))
        
        
        return render(request, 'currentStatus.html', data_view.to_dict())
    
    # Si la solicitud no es un POST, simplemente renderiza la página sin datos
    return render(request, 'currentStatus.html')


def get_recent_data(request):

    if request.method == 'GET':

        latest_record_sensors = SensorsData.objects.using('sensorDB').aggregate(Max('id'))
        max_id_sensors = latest_record_sensors['id__max']
        latest_record_vdf = VdfData.objects.using('sensorDB').aggregate(Max('id'))
        max_id_vdf = latest_record_vdf['id__max']


        # Consultar registro con ese id 
        item_sensors = SensorsData.objects.using('sensorDB').get(id=max_id_sensors)
        item_vdf = VdfData.objects.using('sensorDB').get(id=max_id_vdf)
        data = [round(item_sensors.q1, 2), round(item_sensors.qf, 2), round(item_sensors.pt1, 2), round(item_vdf.powerc, 2), round(item_vdf.fref, 2), round((item_vdf.freal/item_vdf.fref) * ( 100 ) , 2 ) , round((item_vdf.freal/item_vdf.fref) * ( 100 ), 2) , round(item_vdf.powerc, 2)]

    


        return JsonResponse(data, safe=False)