from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages

from applications.currentstatus.scheduler import reschedule_historiadores
from applications.getdata.forms import SensorsDataForm, VdfDataForm
from applications.getdata.models import IntervalosDeActualizacion, Simulador
from applications.settings.forms import FugasConfigForm, SemaforoEstadoForm
from applications.settings.models import FugasConfig, SemaforoEstado





class AdminFormHandlersMixin:
    def handle_sistema_interval(self, request):
        try:
            sistema = int(request.POST["sistema"])
            ints = IntervalosDeActualizacion.objects.latest("id")
            ints.sistema = sistema
            ints.save()

            reschedule_historiadores()          # ← ¡un solo disparo!
            messages.success(request, "Intervalo de sensores actualizado.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect(reverse_lazy("settings:admin_page"))

    def handle_semaforo_interval(self, request):
        try:
            semaforo = int(request.POST["semaforo"])
            ints = IntervalosDeActualizacion.objects.latest("id")
            ints.semaforo = semaforo
            ints.save()

            reschedule_historiadores()          # ← idem
            messages.success(request, "Intervalo del semáforo actualizado.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect(reverse_lazy("settings:admin_page"))

    def handle_semaforo_form_interval(self, request):
        try:
            semaforo = int(request.POST.get('semaforo'))
            intervalos = IntervalosDeActualizacion.objects.latest('id')
            intervalos.semaforo = semaforo
            intervalos.save()
            reschedule_historiadores(semaforo)
        except Exception as e:
            print(f"Error al actualizar semáforo: {e}")
        return redirect(reverse_lazy('settings:admin_page'))

    def handle_simulador_data(self, request):
        vdf_form = VdfDataForm(request.POST)
        sensors_form = SensorsDataForm(request.POST)

        if vdf_form.is_valid() and sensors_form.is_valid():
            vdf_data = {"ts": str(timezone.now()), **vdf_form.cleaned_data}
            sensors_data = {"ts": str(timezone.now()), **sensors_form.cleaned_data}

            simulador = Simulador.objects.order_by('-id').first()

            if simulador:
                # Actualizar los campos necesarios
                simulador.vdf_data = vdf_data
                simulador.sensors_data = sensors_data
                simulador.save()
            else:
                # Si no existe ningún registro, crearlo
                Simulador.objects.create(
                    vdf_data=vdf_data,
                    sensors_data=sensors_data
                )
            return redirect(reverse_lazy('settings:simulador'))
        else:
            context = self.get_context_data(
                vdf_form=vdf_form,
                sensors_form=sensors_form
            )
            return self.render_to_response(context)

    def handle_fugas_config(self, request):
        config = FugasConfig.objects.first()
        form = FugasConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración de fugas actualizada.")
        return redirect(reverse_lazy('settings:admin_page'))

    def handle_semaforo_estado(self, request):
        semaforo = SemaforoEstado.objects.first()
        form = SemaforoEstadoForm(request.POST, instance=semaforo)
        if form.is_valid():
            form.save()
            messages.success(request, "Estado del semáforo actualizado.")
        return redirect(reverse_lazy('settings:admin_page'))
