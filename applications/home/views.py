from django.shortcuts import render

from django.views.generic import TemplateView

from applications.getdata.models import Proyecto

# Create your views here.



class HomeView(TemplateView):
    template_name = 'homepage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = Proyecto.objects.all().first()
        if proyecto:
            context['Project']  = proyecto

        if context['Project']:
            context['Projects'] = Proyecto.objects.exclude(pk=context['Project'].pk)
        else:
            context['Projects'] = Proyecto.objects.none()  

        return context