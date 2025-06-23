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
        # Obtener el último proyecto
        project = get_last_project()

        if not project:
            return Response({
                "status": "error",
                "message": "No se encontró un proyecto válido."
            }, status=404)

        try:
            fan = FanAdministrator(project)
            semaforo = Semaforo(fan=fan)
            semaforo.calcular_estado_final(project)

            return Response({
                "status": "success",
                "data": {
                    "detalle_semaforo": semaforo.detalle
                },
                "variables": {
                    # puedes agregar variables adicionales aquí
                }
            })

        except Exception as e:
            traceback.print_exc()
            return Response({
                "status": "error",
                "message": f"Ocurrió un error al calcular el estado del semáforo o ventilador. {str(e)}"
            }, status=500)
    