from django.db import models


# Create your models here.
class SensorData(models.Model):  
   payload = models.FloatField()
   timestamp = models.DateTimeField()
   class Meta:
      db_table = "sensor_data"


class VdfData(models.Model):  
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

class SensorsData(models.Model):  
   # los comentarios con (-->) indica que es el nombre antes de ser renombrado
   id = models.AutoField(primary_key=True) 
   ts = models.DateTimeField()

   pt2 = models.FloatField(verbose_name="Presión total sensor 2 (Pa)") 
   ps2 = models.FloatField(verbose_name="Presión estática sensor 2 (Pa)") 
   densidad2 = models.FloatField(verbose_name="Presión barométrica sensor 2 (Pa)") #  Presión barométrica ventilador(P2) --> densidad2
   q2 = models.FloatField(verbose_name="Temperatura seca sensor 2 (°C)") # humedad relativa en la frente(hrf) --> (q2)
   
   pt1 = models.FloatField(verbose_name="Humedad Relativa sensor 2 (%)") 
   ps1 = models.FloatField(verbose_name="Presión total sensor 1 (Pa)")
   densidad1 = models.FloatField(verbose_name="Pesión estática sensor 1 (Pa)") # P1 --> densidad1 
   q1 = models.FloatField(verbose_name="Presión barométrica sensor 1 (Pa)")
   lc = models.FloatField(verbose_name="Temperatura seca sensor 2 (°C)") # temperatura seca de la frente (tbs2) --> lc
   qf = models.FloatField(verbose_name="Humedad Relativa sensor 1 (%)")
   k = models.FloatField(verbose_name="factor de fricción")
   tbs = models.FloatField(verbose_name="temperatura seca") # temperatura bulbo seco
   hr = models.FloatField(verbose_name="humedad relativa") # humedad relativa
   tbh = models.FloatField() # temperatura bulmo humedo
   tgbh = models.FloatField()

   
   
   class Meta:
      db_table = "sensors_data"

class Evento(models.Model):
   id = models.AutoField(primary_key=True)
   semaforo = models.IntegerField() # estado calculado
   sensor_ahora = models.ForeignKey(SensorsData, on_delete=models.DO_NOTHING, related_name="sensor_ahora" )
   sensor_hace30m = models.ForeignKey(SensorsData, on_delete=models.DO_NOTHING, related_name="sensor_hace30m" )

   class Meta:
      db_table = "evento"
   




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
   factor_choque = models.FloatField()
   cantidad = models.IntegerField(default=0)

   def __str__(self) -> str:
      return f"{self.nombre} - {self.factor_choque}"

class Tipo_Equipamiento_Diesel(models.Model):
   id = models.AutoField(primary_key=True)
   nombre = models.CharField()

   def __str__(self) -> str:
      return self.nombre

class Sistema_Partida(models.Model):
   id = models.AutoField(primary_key=True)
   nombre = models.CharField()

   def __str__(self) -> str:
      return self.nombre

############################################
class Ventilador(models.Model):
   id = models.AutoField(primary_key=True)
   idu = models.CharField(default='')
   modelo = models.CharField()
   vmm = models.FloatField()
   amm = models.FloatField()
   nmm = models.FloatField()
   hp = models.FloatField()
   polos = models.IntegerField()
   img_ventilador = models.ImageField(upload_to='ventilador/', default='ventilador/vent-def.png')
   accesorios = models.ManyToManyField(Caracteristicas_Ventilador)
   class Meta:
      db_table = "ventilador"

   def __str__(self) -> str:
      return f"{self.modelo}"

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

   def __str__(self) -> str:
      return f"Nomb: {self.ventilador} - ang: {self.angulo} - rpm: {self.rpm}"

class Ducto(models.Model):
   DUCTO_CHOICES = (
      ('circular','Circular'),
      ('ovalado','Ovalado'),
   )
   id = models.AutoField(primary_key=True)
   idu = models.CharField(default='')
   t_ducto = models.CharField(max_length=10, choices=DUCTO_CHOICES)
   diametro = models.IntegerField(null=True, blank=True)
   area = models.FloatField(null=True, blank=True)
   f_friccion = models.FloatField()
   f_fuga = models.FloatField()
   t_acople = models.CharField()
   largo = models.FloatField()
   Ldsf = models.IntegerField()      
   
   class Meta:
      db_table = "ducto"

   def __str__(self) -> str:
      return f"Nomb: {self.t_ducto} \n f friccion:{self.f_friccion} \n f fuga:{self.f_fuga}"


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

   def __str__(self) -> str:
      return f"{self.tipo} - {self.modelo_diesel} - {self.potencia}"

##################################################
class Proyecto(models.Model):
   n_carga_choices = (
      ('liviana','Liviana'),
      ('moderada','Moderada'),
      ('pesada','Pesada')
   )
   t_trabajo_choices = (
      ('trabajo continuo','Trabajo continuo'),
      ('75-25','75% trabajo - 25%'),
      ('50-50','50% trabajo - 50%'),
      ('25-75','25% trabajo - 75%'),
   )
   ventilador = models.ForeignKey(Ventilador, on_delete=models.CASCADE) 
   curva_diseno = models.ForeignKey(CurvaDiseno, on_delete=models.CASCADE)
   ducto = models.ForeignKey(Ducto, on_delete=models.CASCADE)
   equipamientos = models.ManyToManyField(EquipamientoDiesel)
   codos = models.IntegerField()
   caudal_requerido = models.FloatField()
   ancho_galeria = models.FloatField()
   alto_galeria = models.FloatField()
   area_galeria = models.FloatField()
   nivel_carga  = models.CharField(max_length=12, choices=n_carga_choices)
   tipo_trabajo = models.CharField(max_length=16, choices=t_trabajo_choices)
   factor = models.FloatField()
   potencia = models.FloatField()
   dis_e_sens = models.FloatField()
   lf = models.FloatField() # longitud de ducto desde el sensor 2 hasta la frente en metros
   s_partida = models.ForeignKey(Sistema_Partida, on_delete=models.CASCADE) 

   class Meta:
      db_table = "proyecto"