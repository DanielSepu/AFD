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


class SetParams(models.Model):  # Asegúrate de heredar de models.Model
   id = models.AutoField(primary_key=True) 
   ts = models.DateTimeField()
   fref = models.FloatField() 

   class Meta:
      db_table = "set_params"


##################################################
#Tablas estaticas
      
class Caracteristicas_Ventilador(models.Model):
   id = models.AutoField(primary_key=True)
   nombre = models.CharField()

class Tipo_Equipamiento_Diesel(models.Model):
   id = models.AutoField(primary_key=True)
   nombre = models.CharField()

class Sistema_Partida(models.Model):
   id = models.AutoField(primary_key=True)
   nombre = models.CharField()

############################################
class Ventilador(models.Model):
   id = models.AutoField(primary_key=True)
   idu = models.CharField(default='')
   modelo = models.CharField()
   vmm = models.FloatField()
   amm = models.FloatField()
   rmm = models.FloatField()
   hp = models.FloatField()
   polos = models.IntegerField()
   accesorios = models.ManyToManyField(Caracteristicas_Ventilador)
   class Meta:
      db_table = "ventilador"

class CurvaDiseno(models.Model):
   id = models.AutoField(primary_key=True)
   idu = models.CharField(default='')
   ventilador = models.ForeignKey(Ventilador, on_delete=models.CASCADE)
   angulo = models.FloatField()
   rpm = models.FloatField()
   densidad = models.FloatField()
   datos_curva = models.JSONField()
   class Meta:
      db_table = "curva_diseno"

class Ducto(models.Model):
   id = models.AutoField(primary_key=True)
   idu = models.CharField(default='')
   t_ducto = models.CharField()
   f_friccion = models.FloatField()
   f_fuga = models.CharField()
   t_acople = models.CharField()
   largo = models.FloatField()
   class Meta:
      db_table = "ducto"

class EquipamientoDiesel(models.Model):
   id = models.AutoField(primary_key=True)
   idu = models.CharField(default='')
   tipo = models.ForeignKey(Tipo_Equipamiento_Diesel,on_delete=models.CASCADE)
   modelo_diesel = models.CharField()
   potencia = models.FloatField() 
   qr_fabricante = models.FloatField(null=True)
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
   factor = models.FloatField()

   s_partida = models.ForeignKey(Sistema_Partida, on_delete=models.CASCADE) 

   class Meta:
      db_table = "proyecto"