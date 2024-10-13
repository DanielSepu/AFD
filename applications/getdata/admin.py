from django.contrib import admin

from applications.getdata.models import Caracteristicas_Ventilador, CurvaDiseno, SensorsData, Sistema_Partida, Tipo_Equipamiento_Diesel

# Register your models here.


admin.site.register(Caracteristicas_Ventilador)
admin.site.register(Sistema_Partida)
admin.site.register(SensorsData)
admin.site.register(Tipo_Equipamiento_Diesel)
admin.site.register(CurvaDiseno)