from django.db import models

# Create your models here.
class SensorsData(models.Model):  # Asegúrate de heredar de models.Model
   id = models.AutoField(primary_key=True) 
   ts = models.DateTimeField()
   pt2 = models.FloatField() 
   ps2 = models.FloatField() 
   densidad2 = models.FloatField()
   q2 = models.FloatField()
   pt1 = models.FloatField()
   ps1 = models.FloatField()
   densidad1 = models.FloatField()
   q1 = models.FloatField()
   lc = models.FloatField()
   qf = models.FloatField()

   class Meta:
      db_table = "sensors_data"