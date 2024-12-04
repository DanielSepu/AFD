from django.shortcuts import render

from django.views.generic import TemplateView

from applications.getdata.models import Proyecto
from applications.home.functions import get_last_project
from modules.semaforo import Semaforo

# Create your views here.

class HomeView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = None
        try:
            proyecto = get_last_project()
        except Exception as e:
            pass
        if proyecto:
            context['Project']  = proyecto 
            context['Projects'] = Proyecto.objects.exclude(pk=context['Project'].pk)
        
            semaforo= Semaforo(self.request)
            semaforo.calcular_estado_final(proyecto)
            context["detalle_semaforo"]=semaforo.detalle
        
        return context