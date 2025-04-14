
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime

from applications.currentstatus.mixin import procesar_datos_sensores
from applications.getdata.models import IntervalosDeActualizacion
from core.logger_config import logger_AFD

logger = logging.getLogger(__name__)

# Instancia global del scheduler y de la tarea
scheduler = BackgroundScheduler()
SENSOR_JOB_ID = 'sensor_job'
SISTEMA_JOB_ID = 'sistema_job'

def sensor_job():
    # Llama a la función que procesa los datos del sensor
    resultado = procesar_datos_sensores()
    logger.info(f"Sensor job executed at {datetime.now()}, resultado: {resultado}")

def sistema_job():
    # Llama a la función que procesa los datos del sensor
    resultado = procesar_datos_sensores()
    logger.info(f"Sensor job executed at {datetime.now()}, resultado: {resultado}")
    
def start_scheduler():
    """
    Inicia el scheduler y programa la tarea con un intervalo por defecto.
    """
    # Intervalo inicial, por ejemplo, 300 segundos
    default_interval = 300
    intervalos = IntervalosDeActualizacion.objects.latest('id')
    
    # Si ya existe el job, se elimina para evitar duplicados.
    try:
        scheduler.remove_job(SENSOR_JOB_ID)
        # scheduler.remove_job(SISTEMA_JOB_ID)
    except Exception:
        pass
    
    scheduler.add_job(
        sensor_job,
        trigger=IntervalTrigger(seconds=intervalos.sistema),
        id=SENSOR_JOB_ID,
        replace_existing=True
    )
    scheduler.start()
    
    """scheduler.add_job(
        sistema_job,
        trigger=IntervalTrigger(seconds=intervalos.semaforo),
        id=SISTEMA_JOB_ID,
        replace_existing=True
    )
    scheduler.start()
    """
    logger_AFD.debug(f"Worker simulador ")
    logger_AFD.debug(f"{scheduler.print_jobs()}")
    logger.info("Scheduler started with sensor_job at interval %s seconds", default_interval)

def update_sensor_job_interval(new_interval):
    """
    Actualiza el intervalo de ejecución del sensor_job.
    """
    try:
        job = scheduler.get_job(SENSOR_JOB_ID)
        if job:
            # Reschedule la tarea con el nuevo intervalo
            job.reschedule(trigger=IntervalTrigger(seconds=new_interval))
            logger.info("Sensor job interval updated to %s seconds", new_interval)
        else:
            # Si no existe el job, se crea uno nuevo
            scheduler.add_job(
                sensor_job,
                trigger=IntervalTrigger(seconds=new_interval),
                id=SENSOR_JOB_ID,
                replace_existing=True
            )
            logger.info("Sensor job created with new interval %s seconds", new_interval)
    except Exception as e:
        logger.error("Error al actualizar el intervalo del sensor job: %s", e)



def update_sistema_job_interval(new_interval):
    """
    Actualiza el intervalo de ejecución del sensor_job.
    """
    try:
        job = scheduler.get_job(SISTEMA_JOB_ID)
        if job:
            # Reschedule la tarea con el nuevo intervalo
            job.reschedule(trigger=IntervalTrigger(seconds=new_interval))
            logger.info("Sistema job interval updated to %s seconds", new_interval)
        else:
            # Si no existe el job, se crea uno nuevo
            scheduler.add_job(
                sistema_job,
                trigger=IntervalTrigger(seconds=new_interval),
                id=SISTEMA_JOB_ID,
                replace_existing=True
            )
            logger.info("Sistema job created with new interval %s seconds", new_interval)
    except Exception as e:
        logger.error("Error al actualizar el intervalo del sensor job: %s", e)
