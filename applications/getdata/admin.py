from django.contrib import admin

from applications.getdata.models import Caracteristicas_Ventilador, SensorsData, Sistema_Partida

# Register your models here.


admin.site.register(Caracteristicas_Ventilador)
admin.site.register(Sistema_Partida)
admin.site.register(SensorsData)