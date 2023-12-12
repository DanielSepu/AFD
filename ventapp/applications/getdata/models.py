from django.db import models

# Create your models here.
class SensorData(models.Model):  # Asegúrate de heredar de models.Model
   id = models.AutoField(primary_key=True) 
   payload = models.FloatField()
   timestamp = models.DateTimeField()
   class Meta:
      db_table = "sensor_data"