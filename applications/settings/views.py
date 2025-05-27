from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core import serializers
from django.views import View
from django.views.generic import DeleteView, TemplateView
from django.contrib import messages
import json

from applications.getdata.forms import SemaforoForm, SensorsDataForm, SimuladorForm, SistemaForm, VdfDataForm
from applications.getdata.models import *
from applications.dbs.forms import *
from applications.settings.forms import FugasConfigForm, SemaforoEstadoForm
from applications.settings.mixins import AdminFormHandlersMixin
from applications.settings.models import FugasConfig, SemaforoEstado

def settings(request):
   setting_type = request.GET.get('type')
   if request.method == 'GET':
      if setting_type == 'new_project' or setting_type is None:
         form = ProyectoForm()
         context = {'setting_type': setting_type, 'form': form, 'equipamientos': EquipamientoDiesel.objects.all()}
         return render(request, 'widgets/settings/newProject.html', context)
      
      if setting_type == 'current_project':
         up = Proyecto.objects.all().order_by('id').last()
         
         if up is not None:
            up_eqp = up.equipamientos.all()
            form = ProyectoForm(instance=up)
            context = {'exist': True, 'setting_type': setting_type, 'form': form, 'id': up.id, 'up_eqp': up_eqp, 'equipamientos': EquipamientoDiesel.objects.all()}
         else:
            # Manejo de cuando no hay proyectos
            up_eqp = None
            form = ProyectoForm()

            context = {'exist':False,'setting_type': setting_type, 'form': form, 'up_eqp': up_eqp, 'equipamientos': EquipamientoDiesel.objects.all(), 'message': 'No hay proyectos disponibles.'}
         
         return render(request, 'widgets/settings/currentProject.html', context)

   
   if request.method == 'POST':
      if setting_type == 'new_project':
         form = ProyectoForm(request.POST) 
         context = {'setting_type': setting_type, 'form': form}

         if form.is_valid():
            proyecto = form.save()
            proy = Proyecto.objects.get(id=proyecto.id)
            for k,v in enumerate(EquipamientoDiesel.objects.all()): #For para guardar foreing key desde checklist que fue creado a mano por style
               if request.POST.get('eq_'+str(v.id)):
                  proy.equipamientos.add(v)
            proy.save()
         else:
            print("Error el formulario no es valido")
            print(form.errors)
         return redirect('settings:settings')

      if setting_type == 'current_project':
         proy = Proyecto.objects.get(id=request.POST.get('id'))
         form = ProyectoForm(request.POST,instance=proy)

         if form.is_valid():
            form.save()
            proy.equipamientos.clear()
            for k,v in enumerate(EquipamientoDiesel.objects.all()): #Mismo For para foreing keys desde checklist con style no manejado por django
               if request.POST.get('eq_'+str(v.id)):
                  proy.equipamientos.add(v)
            proy.save()
         
         return redirect(reverse('settings:settings') + '?type=current_project')

      if setting_type == 'new_project_2':
         task=request.POST.get('task')
         cd = CurvaDiseno.objects.filter(ventilador_id=task)
         cdpk = json.loads(serializers.serialize('json', cd, fields=("id", "idu")))
         return JsonResponse({'cdpk':cdpk})
      
      if setting_type == 'new_project_3':
         task=request.POST.getlist('task[]')
         sumatoria = 0
         for i in task:
            eq = EquipamientoDiesel.objects.get(id=i)
            sumatoria += eq.qr_calculado
         return JsonResponse({'sumatoria':sumatoria})


class ProjectDelete(DeleteView):
    model = Proyecto
    success_url = reverse_lazy('/') 
    template_name = 'widgets/settings/confirm_delete.html'
   

class AdminPageView(TemplateView, AdminFormHandlersMixin):
    template_name = 'widgets/manager/pages/admin_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            simulador_json = Simulador.objects.latest('-id')
        except Simulador.DoesNotExist:
            simulador_json = None

        vdf_initial = simulador_json.data.get('vdf_data', {}) if simulador_json else {}
        sensors_initial = simulador_json.data.get('sensors_data', {}) if simulador_json else {}
        intervalos = IntervalosDeActualizacion.objects.last()

        context.update({
            "semaforo_form": SemaforoForm(instance=intervalos),
            "sistema_form": SistemaForm(instance=intervalos),
            "vdf_form": VdfDataForm(initial=vdf_initial),
            "sensors_form": SensorsDataForm(initial=sensors_initial),
            "simuladorjson_form": SimuladorForm(instance=simulador_json) if simulador_json else SimuladorForm(),
            "simulador_json_data": simulador_json.data if simulador_json else None,
            "config_form": FugasConfigForm(instance=FugasConfig.objects.first()),
            "semaforo_estado_form": SemaforoEstadoForm(instance=SemaforoEstado.objects.first())
        })
        return context
     
     
    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type")

        handler_map = {
            'semaforo': self.handle_semaforo_interval,
            'sistema': self.handle_sistema_interval,
            'semaforo_form': self.handle_semaforo_form_interval,
            'simulador': self.handle_simulador_data,
            'fugas': self.handle_fugas_config,
            'semaforo_estado': self.handle_semaforo_estado,
        }

        handler = handler_map.get(form_type)
        if handler:
            return handler(request)

        return redirect(reverse_lazy('settings:admin_page'))
class ConfigSemaforoView(TemplateView):
    template_name = 'widgets/manager/pages/config_semaforo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semaforo_form'] = SemaforoForm()  # instancia del formulario
        return context

    def post(self, request, *args, **kwargs):
        form = SemaforoForm(request.POST)
        if form.is_valid():
            form.save()
            # puedes agregar un mensaje o redirección
        context = self.get_context_data()
        context['semaforo_form'] = form
        return redirect(reverse('settings:admin_page'))


class SimuladorView(TemplateView):
    template_name = 'widgets/manager/pages/simulador.html'

class RangoHistorialView(TemplateView):
    template_name = 'widgets/manager/pages/rango_historial.html'
    
   
class ConfiguracionAlertasView(TemplateView):
    template_name = "widgets/settings/semaforo/alertas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config_form"] = FugasConfigForm(instance=FugasConfig.objects.first())
        context["semaforo_estado_form"] = SemaforoEstadoForm(instance=SemaforoEstado.objects.first())
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type")
        if form_type == "fugas":
            config = FugasConfig.objects.first()
            form = FugasConfigForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, "Configuración de fugas actualizada correctamente.")
        elif form_type == "semaforo_estado":
            semaforo = SemaforoEstado.objects.first()
            form = SemaforoEstadoForm(request.POST, instance=semaforo)
            if form.is_valid():
                form.save()
                messages.success(request, "Estado del semáforo actualizado correctamente.")
        return redirect(reverse_lazy("settings:admin_page"))


class DesbloquearSemaforoView(View):
    def post(self, request, *args, **kwargs):
        semaforo = SemaforoEstado.objects.first()
        if semaforo and semaforo.esta_bloqueado:
            semaforo.esta_bloqueado = False
            semaforo.color_actual = "verde"
            semaforo.motivo_bloqueo = ""
            semaforo.save()
            messages.success(request, "El semáforo ha sido desbloqueado manualmente.")
        else:
            messages.info(request, "El semáforo ya está activo o no existe.")
        return redirect(reverse_lazy("settings:admin_page"))