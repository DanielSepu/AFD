from django.contrib import admin

from applications.getdata.models import Caracteristicas_Ventilador, CurvaDiseno, Ducto, Proyecto, SensorsData, Sistema_Partida, Tipo_Equipamiento_Diesel, VdfData, Ventilador

# Register your models here.

admin.site.register(Caracteristicas_Ventilador)
admin.site.register(Sistema_Partida)
admin.site.register(SensorsData)
admin.site.register(Tipo_Equipamiento_Diesel)
admin.site.register(CurvaDiseno)
admin.site.register(Ventilador)
admin.site.register(VdfData) 
admin.site.register(Ducto) 
admin.site.register(Proyecto) 



