
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime

from applications.currentstatus.mixin import procesar_datos_sensores
from applications.getdata.models import IntervalosDeActualizacion
from applications.home.functions import get_last_project
from core.logger_config import logger_AFD
from modules.semaforo import Semaforo


# Instancia global del scheduler y de la tarea
scheduler = BackgroundScheduler()
SENSOR_JOB_ID = 'sensor_job'
SISTEMA_JOB_ID = 'sistema_job'

def sensor_job():
    # Llama a la función que procesa los datos del sensor
    resultado = procesar_datos_sensores()
    logger_AFD.info(f"Se actualizaron los datos del historial en {datetime.now()} ")

def sistema_job():
    project = get_last_project()
    semaforo= Semaforo()
    context = {}
    try:
        semaforo.calcular_estado_final(project)
        #logger_AFD.info(semaforo)
        context["detalle_semaforo"]=semaforo.detalle
    except Exception as e:
        traceback.print_exc()
    logger_AFD.info("Se actualizo el semaforo %s", datetime.now())


def start_scheduler():
    """
    Inicia el scheduler y programa ambas tareas con los intervalos definidos en la base de datos.
    """
    # Obtiene los intervalos más recientes
    intervalos = IntervalosDeActualizacion.objects.latest('id')
    
    # Remover jobs existentes para evitar duplicados.
    try:
        scheduler.remove_job(SENSOR_JOB_ID)
    except Exception:
        pass
    try:
        scheduler.remove_job(SISTEMA_JOB_ID)
    except Exception:
        pass
    
    if intervalos.sistema != None:
        
        # Agregar job para sensor_job, usando el intervalo definido en intervalos.sistema
        scheduler.add_job(
            sensor_job,
            trigger=IntervalTrigger(seconds=intervalos.sistema),
            id=SENSOR_JOB_ID,
            replace_existing=True
        )
        
    else:
        logger_AFD.debug("el worker del sistema no esta activo")
    
    if intervalos.semaforo != None:
        # Agregar job para sistema_job, usando el intervalo definido en intervalos.semaforo
        scheduler.add_job(
            sistema_job,
            trigger=IntervalTrigger(seconds=intervalos.semaforo),
            id=SISTEMA_JOB_ID,
            replace_existing=True
        )
    else:
        logger_AFD.debug("el worker simulador del sensor no esta activo")
    
    # Iniciar el scheduler (si aún no está en ejecución)
    if not scheduler.running:
        scheduler.start()
    
    logger_AFD.debug("~~ Worker simulador activado ~~")
    logger_AFD.info("Scheduler iniciado: sensor_job intervalos %s segundos, sistema_job intervalo %s segundos", intervalos.sistema, intervalos.semaforo)
    logger_AFD.debug(scheduler.print_jobs())
    


def start_semaforo_job():
    """
    Inicia o reinicia el nuevo job con un intervalo específico.
    """
    new_interval = 600  # Intervalo en segundos (por ejemplo, 600 segundos = 10 minutos)

    # Se intenta remover el job si ya existe para evitar duplicados
    try:
        scheduler.remove_job(SISTEMA_JOB_ID)
    except Exception:
        pass

    # Agrega el nuevo job al scheduler
    scheduler.add_job(
        new_job,
        trigger=IntervalTrigger(seconds=new_interval),
        id=SISTEMA_JOB_ID,
        replace_existing=True
    )
    
    logger_AFD.info("New job scheduled at interval %s seconds", new_interval)


def update_sensor_job_interval(new_interval):
    """
    Actualiza el intervalo de ejecución del sensor_job.
    """
    try:
        job = scheduler.get_job(SENSOR_JOB_ID)
        if job:
            # Reschedule la tarea con el nuevo intervalo
            job.reschedule(trigger=IntervalTrigger(seconds=new_interval))
            logger_AFD.info("Sensor job interval updated to %s seconds", new_interval)
        else:
            # Si no existe el job, se crea uno nuevo
            scheduler.add_job(
                sensor_job,
                trigger=IntervalTrigger(seconds=new_interval),
                id=SENSOR_JOB_ID,
                replace_existing=True
            )
            logger_AFD.info("Sensor job created with new interval %s seconds", new_interval)
    except Exception as e:
        logger_AFD.error("Error al actualizar el intervalo del sensor job: %s", e)



def update_semaforo_job_interval(new_interval):
    """
    Actualiza el intervalo de ejecución del sensor_job.
    """
    try:
        job = scheduler.get_job(SISTEMA_JOB_ID)
        if job:
            # Reschedule la tarea con el nuevo intervalo
            job.reschedule(trigger=IntervalTrigger(seconds=new_interval))
            logger_AFD.info("Sistema job interval updated to %s seconds", new_interval)
        else:
            # Si no existe el job, se crea uno nuevo
            scheduler.add_job(
                sistema_job,
                trigger=IntervalTrigger(seconds=new_interval),
                id=SISTEMA_JOB_ID,
                replace_existing=True
            )
            logger_AFD.info("Sistema job actualizado con nuevo interval %s seconds", new_interval)
    except Exception as e:
        logger_AFD.error("Error al actualizar el intervalo del sensor job: %s", e)
