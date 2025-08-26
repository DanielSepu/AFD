from django.contrib import admin

from applications.getdata.models import *

# Register your models here.

class SensorsDataAdmin(admin.ModelAdmin):
    list_display = ('ts', 'pt2', 'ps2', 'Pbs2','Tbs2')  # ¿Qué campos te interesa ver?
    search_fields = ('pt2', 'ps2')         # ¿Qué campos deben ser buscables?
    list_filter = ('pt2',)                     # ¿Quieres filtrar por algún campo?
    ordering = ('ts',)                          # ¿Cuál debería ser el orden?

class HistorialAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Historial._meta.get_fields()]
    search_fields = [field.name for field in Historial._meta.get_fields() if field.get_internal_type() in ['CharField', 'TextField', 'FloatField']]
    list_filter = ('ts', 'creado_en')
    ordering = ('-ts',)                        


admin.site.register(Caracteristicas_Ventilador)
admin.site.register(Sistema_Partida)
admin.site.register(SensorsData, SensorsDataAdmin)
admin.site.register(Tipo_Equipamiento_Diesel)
admin.site.register(EquipamientoDiesel)
admin.site.register(CurvaDiseno)
admin.site.register(Ventilador)
admin.site.register(VdfData) 
admin.site.register(Ducto) 
admin.site.register(Simulador) 
admin.site.register(Proyecto) 
admin.site.register(Historial, HistorialAdmin)



