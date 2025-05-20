from django.db import models
from django.core import serializers
import json

# Create your models here.

class SemaforoEstado(models.Model):
    nombre = models.CharField(max_length=100, default="Semáforo General")
    color_actual = models.CharField(max_length=10, choices=[("verde", "Verde"), ("amarillo", "Amarillo"), ("rojo", "Rojo")], default="verde")
    esta_bloqueado = models.BooleanField(default=False)
    motivo_bloqueo = models.TextField(blank=True, null=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.color_actual} - {'Bloqueado' if self.esta_bloqueado else 'Activo'}"
    
class FugasConfig(models.Model):
    nombre = models.CharField(max_length=100, default="Configuración general")
    presion_promedio = models.FloatField(help_text="Promedio de presión normal del sistema (en pt1)")
    tolerancia_minima = models.FloatField(help_text="Porcentaje mínimo tolerado de caída (ej. 5 = 5%)")
    tolerancia_maxima = models.FloatField(help_text="Porcentaje máximo tolerado (ej. 5 = 5%)")
    alerta_activa = models.BooleanField(default=True)
    sistema_bloqueado = models.BooleanField(default=False)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre