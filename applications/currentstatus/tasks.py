

from celery import shared_task
from applications.currentstatus.mixin import procesar_datos_sensores


@shared_task(bind=True)
def schedule_sensor_processing(self, interval):
    """
    Tarea de Celery que ejecuta 'procesar_datos_sensores' y se reprograme automáticamente
    después de 'interval' segundos.
    
    :param interval: Intervalo de tiempo en segundos entre ejecuciones.
    """
    # Ejecuta la función de procesamiento

    resultado = procesar_datos_sensores()
    
    # Reprograma la tarea para que se ejecute nuevamente después de 'interval' segundos.
    self.apply_async(args=[interval], countdown=interval)
    
    return resultado

