from rest_framework.response import Response
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
        semaforo= Semaforo()
        semaforo.calcular_estado_final(project)
        context = {}
        context["detalle_semaforo"]=semaforo.detalle

        return Response(context)
    