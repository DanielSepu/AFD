from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core import serializers
from django.views.generic import DeleteView, TemplateView
import json

from django.utils import timezone
from applications.currentstatus.scheduler import update_sensor_job_interval
from applications.currentstatus.tasks import schedule_sensor_processing
from applications.getdata.forms import SemaforoForm, SensorsDataForm, SimuladorForm, SistemaForm, VdfDataForm
from applications.getdata.models import *
from applications.dbs.forms import *

def settings(request):
   setting_type = request.GET.get('type')
   print(request.method)
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
   

class AdminPageView(TemplateView):
    template_name = 'widgets/manager/pages/admin_page.html'

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         try:
            simulador_json = Simulador.objects.latest('id')
            
         except Simulador.DoesNotExist:
            simulador_json = None

         
         if simulador_json and simulador_json.data:
            data = simulador_json.data
            # Se asume que en el campo JSON se almacenaron:
            # - datos para el semáforo bajo la clave 'semaforo_data'
            # - datos para VdfData bajo la clave 'vdf_data'
            # - datos para SensorsData bajo la clave 'sensors_data'
            vdf_initial = data.get('vdf_data', {})
            sensors_initial = data.get('sensors_data', {})
         else:

            vdf_initial = {}
            sensors_initial = {}

         intervalos = IntervalosDeActualizacion.objects.last()
         context['semaforo_form'] = SemaforoForm(instance=intervalos)
         context['sistema_form'] = SistemaForm(instance=intervalos)
         context['vdf_form'] = VdfDataForm(initial=vdf_initial)
         context['sensors_form'] = SensorsDataForm(initial=sensors_initial)
         context['simuladorjson_form'] = SimuladorForm(instance=simulador_json) if simulador_json else SimuladorForm()
         context['simulador_json_data'] = simulador_json.data if simulador_json else None
         return context

    def post(self, request, *args, **kwargs):
        # Se utiliza un campo oculto en cada formulario para identificar cuál se envía.
        
        form_type = request.POST.get('form_type')
        
        if form_type == 'semaforo':
            semaforo_form = SemaforoForm(request.POST)
            if semaforo_form.is_valid():
                # Aquí se procesa y guarda la configuración del semáforo.
              
                update_interval = semaforo_form.cleaned_data['update_interval']
                # Lógica de guardado (por ejemplo, guardarlo en la base de datos o en settings)
                # messages.success(request, "Semáforo actualizado correctamente")
                return redirect(reverse('settings:admin_page'))
            else:
                context = self.get_context_data(semaforo_form=semaforo_form)
                return self.render_to_response(context)
        elif form_type == 'sistema':
            # Se asume que el formulario envía el campo "update_interval"
            try:
               sistema = int(request.POST.get('sistema'))
               # Se intenta obtener el último registro. Si no existe, se crea uno.
               # Aquí usamos get_or_create, buscando por algún criterio.
               # Como no tenemos un identificador único, se puede optar por crear uno nuevo
               # si no existe ningún registro en el modelo.
               try:
                     intervalos = IntervalosDeActualizacion.objects.latest('id')
                     intervalos.sistema = sistema
                     intervalos.save()
               except Historial.DoesNotExist:
                     intervalos = IntervalosDeActualizacion.objects.create(sistema=sistema)
               
               # Reprogramar la tarea de Celery con el nuevo intervalo
               # update_sensor_job_interval(update_interval)
               
               # messages.success(request, "Intervalo actualizado correctamente")
               return redirect(reverse('settings:admin_page'))
            except (ValueError, TypeError) as e:
               # Manejo de error: valor no válido para update_interval
               print(f"Ocurrió un error al actualizar el historial: {e}")
               return redirect(reverse('settings:admin_page'))
            
        elif form_type == 'semaforo_form':
            # Se asume que el formulario envía el campo "update_interval"
            try:
               semaforo = int(request.POST.get('semaforo'))
               # Se intenta obtener el último registro. Si no existe, se crea uno.
               # Aquí usamos get_or_create, buscando por algún criterio.
               # Como no tenemos un identificador único, se puede optar por crear uno nuevo
               # si no existe ningún registro en el modelo.
               try:
                     intervalos = IntervalosDeActualizacion.objects.latest('id')
                     intervalos.semaforo = semaforo
                     intervalos.save()
               except Historial.DoesNotExist:
                     intervalos = IntervalosDeActualizacion.objects.create(intervalo=semaforo)
               
               # Reprogramar la tarea de Celery con el nuevo intervalo
               update_sensor_job_interval(update_interval)
               
               # messages.success(request, "Intervalo actualizado correctamente")
               return redirect(reverse('settings:admin_page'))
            except (ValueError, TypeError) as e:
               # Manejo de error: valor no válido para update_interval
               print(f"Ocurrió un error al actualizar el historial: {e}")
               return redirect(reverse('settings:admin_page'))

        elif form_type == 'simulador':
            vdf_form = VdfDataForm(request.POST)
            sensors_form = SensorsDataForm(request.POST)
   
            valid = True
            if not vdf_form.is_valid():
               print("vdf_form no válidos")
               valid = False
            if not sensors_form.is_valid():
               print("sensors_form no válidos")
               valid = False
            

            if valid:
               # Extrae los datos de cada formulario sin guardar en el modelo individual
               vdf_data = {
                     "ts": str(timezone.now()),
                     "fref": vdf_form.cleaned_data['fref'],
                     "freal": vdf_form.cleaned_data['freal'],
                     "vf": vdf_form.cleaned_data['vf'],
                     "oc": vdf_form.cleaned_data['oc'],
                     "power": vdf_form.cleaned_data['power'],
                     "powerc": vdf_form.cleaned_data['powerc'],
                     "rpm": vdf_form.cleaned_data['rpm'],
               }
               sensors_data = {
                     "ts": str(timezone.now()),
                     "pt2": sensors_form.cleaned_data['pt2'],
                     "ps2": sensors_form.cleaned_data['ps2'],
                     "Pbs2": sensors_form.cleaned_data['Pbs2'],
                     "Tbs2": sensors_form.cleaned_data['Tbs2'],
                     "HRs2": sensors_form.cleaned_data['HRs2'],
                     "pt1": sensors_form.cleaned_data['pt1'],
                     "ps1": sensors_form.cleaned_data['ps1'],
                     "Pbs1": sensors_form.cleaned_data['Pbs1'],
                     "Tbs1": sensors_form.cleaned_data['Tbs1'],
                     "HRs1": sensors_form.cleaned_data['HRs1'],
               }

               # simuladorjson_instance = simuladorjson_form.save(commit=False)
               data_simulador = {
                     "vdf_data": vdf_data,
                     "sensors_data": sensors_data,
               }
               simuladorjson_instance = Simulador()
               simuladorjson_instance.data = data_simulador
               simuladorjson_instance.save()
               print(f"Se guardaron los datos en data: {simuladorjson_instance.data}")
               return redirect(reverse('settings:simulador'))
            else:
               print("Datos no válidos")
               context = self.get_context_data(
                     vdf_form=vdf_form,
                     sensors_form=sensors_form,
                     simuladorjson_form=data_simulador
               )
               return self.render_to_response(context)
        # En caso de que no se reconozca el formulario enviado, se redirige a la página principal
        return redirect(reverse('settings:admin_page'))

class ConfigSemaforoView(TemplateView):
    template_name = 'widgets/manager/pages/config_semaforo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semaforo_form'] = SemaforoForm()  # instancia del formulario
        return context

    def post(self, request, *args, **kwargs):
        form = SemaforoForm(request.POST)
        if form.is_valid():
            print(form)
            form.save()
            # puedes agregar un mensaje o redirección
        context = self.get_context_data()
        context['semaforo_form'] = form
        return redirect(reverse('settings:admin_page'))

    
    
       

class SimuladorView(TemplateView):
    template_name = 'widgets/manager/pages/simulador.html'

class RangoHistorialView(TemplateView):
    template_name = 'widgets/manager/pages/rango_historial.html'
    
    
    