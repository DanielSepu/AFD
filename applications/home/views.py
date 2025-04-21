from django.http import JsonResponse
from django.shortcuts import redirect, render

from django.views.generic import TemplateView

from applications.getdata.models import IntervalosDeActualizacion, Proyecto
from applications.home.functions import get_last_project
from modules.semaforo import Semaforo

# Create your views here.

class HomeView(TemplateView):
    template_name = 'homepage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = get_last_project()
        if proyecto:
            context['Project']  = proyecto 
        if context['Project']:
            context['Projects'] = Proyecto.objects.exclude(pk=context['Project'].pk)
        
            semaforo= Semaforo()
            try:
                semaforo.calcular_estado_final(proyecto)
                context["detalle_semaforo"]=semaforo.detalle
            except Exception as e:
                context["detalle_semaforo"]={}
        context["intervalos_sistema"] = IntervalosDeActualizacion.objects.latest('id')
        return context
    
    def post(self, request, *args, **kwargs):
        """ Maneja la actualización del proyecto actual """
        proyecto = get_last_project()
        if not proyecto:
            return JsonResponse({"error": "No hay un proyecto actual para actualizar"}, status=400)

        nombre_nuevo = request.POST.get("nombre")
        if not nombre_nuevo:
            return JsonResponse({"error": "El campo 'nombre' es obligatorio"}, status=400)

        # Actualizar el proyecto con el nuevo nombre
        proyecto.dedf = nombre_nuevo
        proyecto.save()

        return redirect("/")

