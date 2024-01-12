from django.db import models

# Create your models here.
class SensorData(models.Model):  # Asegúrate de heredar de models.Model
   id = models.AutoField(primary_key=True) 
   payload = models.FloatField()
   timestamp = models.DateTimeField()
   class Meta:
      db_table = "sensor_data"

class VdfData(models.Model):  # Asegúrate de heredar de models.Model
   id = models.AutoField(primary_key=True) 
   ts = models.DateTimeField()
   fref = models.FloatField() 
   freal = models.FloatField() 
   vf = models.FloatField()
   oc = models.FloatField(db_column='if')
   power = models.FloatField()
   powerc = models.FloatField()
   rpm = models.FloatField()

   class Meta:
      db_table = "vdf_data"


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
   k = models.FloatField()
   
   class Meta:
      db_table = "sensors_data"




############################################
class Ventilador(models.Model):
   id = models.AutoField(primary_key=True) 
   modelo = models.CharField()
   vmm = models.FloatField()
   amm = models.FloatField()
   rmm = models.FloatField()
   polos = models.IntegerField()
   accesorios = models.CharField()
   class Meta:
      db_table = "ventilador"

class CurvaDiseno(models.Model):
   id = models.AutoField(primary_key=True)
   ventilador = models.ForeignKey(Ventilador, on_delete=models.CASCADE)
   angulo = models.FloatField()
   rpm = models.FloatField()
   densidad = models.FloatField()
   datos_curva = models.JSONField()
   class Meta:
      db_table = "curva_diseno"

class Ducto(models.Model):
   id = models.AutoField(primary_key=True)
   tipo = models.TextField()
   f_friccion = models.FloatField()
   f_fuga = models.TextField()
   tipo = models.TextField()
   largo = models.FloatField()
   class Meta:
      db_table = "ducto"

class EquipamientoDiesel(models.Model):
   id = models.AutoField(primary_key=True)
   tipo = models.TextField()
   modelo_diesel = models.TextField()
   potencia = models.FloatField() 
   qr_fabricante = models.FloatField()
   qr_calculado = models.FloatField()
   class Meta:
      db_table = "equipamiento_diesel"

##################################################

class Proyecto(models.Model):
   ventilador = models.ForeignKey(Ventilador, on_delete=models.CASCADE) 
   curva_diseno = models.ForeignKey(CurvaDiseno, on_delete=models.CASCADE)
   ducto = models.ForeignKey(Ducto, on_delete=models.CASCADE)
   
   equipamientos = models.ManyToManyField(EquipamientoDiesel)
   
   codos = models.IntegerField()
   caudal_requerido = models.FloatField()
   ancho_galeria = models.FloatField()
   alto_galeria = models.FloatField()
   area_galeria = models.FloatField()  
   class Meta:
      db_table = "proyecto"