import traceback
from rest_framework.response import Response
from applications.fanreal.fanAdministrator import FanAdministrator
from applications.home.functions import get_last_project
from modules.semaforo import Semaforo

from rest_framework.views import APIView



class  SemaforoApiView(APIView):
    """
        Clase que representa un API para obtener el estado del semaforo de la ventilacion.
    """
    
    def get(self, request, format=None):
        # Obtener el ultimo proyecto
        project = get_last_project()
        context = {}

        if not project:
            context["error"] = "No se encontró un proyecto válido."
            return Response(context, status=404)

        
        try:
            fan = FanAdministrator(project)
            semaforo = Semaforo(fan=fan)
            semaforo.calcular_estado_final(project)
            context["detalle_semaforo"] = semaforo.detalle
        except Exception as e:
            traceback.print_exc()
            context["error"] = f"Error calculando semaforo: {e}"

        return Response(context)
    