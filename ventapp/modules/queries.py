from applications.getdata.models import SensorData

def get_sensor_data():
   # return SensorData.objects.using('sensorDB').all()
   return SensorData.objects.using('sensorDB').exclude(payload__isnull=True)