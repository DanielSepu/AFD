from applications.getdata.models import SensorData, VdfData, SensorsData
import pandas as pd

def get_sensor_data_db():
   # return SensorData.objects.using('sensorDB').all()
   return SensorData.objects.using('sensorDB').exclude(payload__isnull=True)

def get_10min_vdf_data2(request):
   if request.method == 'GET':
      items = VdfData.objects.using('sensorDB').order_by('-id')[:40]
      data = list(items.values()) 
      return data
   
def get_10min_vdf_data():
   items = VdfData.objects.using('sensorDB').order_by('-id')[:40]
   df = pd.DataFrame(list(items.values()))
   return df

def get_10min_sensor_data():
   items = SensorsData.objects.using('sensorDB').order_by('-id')[:40]
   df = pd.DataFrame(list(items.values()))
   return df