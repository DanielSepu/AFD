from django.db import models

# Create your models here.

class GraficoTolerancia(models.Model):
    TIPO_GRAFICA_CHOICES = [
        ('total_pressure', 'Presión total'),
        ('static_pressure', 'Presión estática'),
        ('power', 'Potencia'),
    ]
    
    TOLERANCIA_CHOICES = [
        ('AN1', 'AN1'),
        ('AN2', 'AN2'),
        ('AN3', 'AN3'),
        ('AN4', 'AN4'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_GRAFICA_CHOICES, unique=True)
    tolerancia = models.CharField(max_length=3, choices=TOLERANCIA_CHOICES, default='AN3')

    class Meta:
        db_table = "graficotolerancia"
        