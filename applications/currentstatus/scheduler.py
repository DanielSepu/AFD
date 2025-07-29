# scheduler.py  (un solo archivo para todo)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pytz import timezone
from django.conf import settings
import logging
import traceback
from datetime import datetime
from applications.fanreal.fanAdministrator import FanAdministrator
from core.logger_config import logger_AFD

# ----------------- Instancia ÚNICA -----------------
scheduler = BackgroundScheduler(
    timezone=timezone("America/Costa_Rica")   # o settings.TIME_ZONE
)

# ----------------- IDs de jobs -----------------
SENSOR_JOB_ID   = "sensor_job"
SISTEMA_JOB_ID  = "sistema_job"
SIMULATOR_JOB_ID = "simulator_job"

# ---------------------------------------------------
# 1. HISTORIADOR - SENSORES
# ---------------------------------------------------
from applications.currentstatus.mixin import procesar_datos_sensores

def sensor_job():
    try:
        procesar_datos_sensores()
        logger_AFD.info("Historial actualizado %s", datetime.now())
    except Exception:
        logger_AFD.exception("Error en sensor_job")

# ---------------------------------------------------
# 2. HISTORIADOR - SEMAFORO
# ---------------------------------------------------
from applications.home.functions import get_last_project
from modules.semaforo import Semaforo

def sistema_job():
    try:
        project  = get_last_project()
        fan = FanAdministrator(project)
        semaforo = Semaforo(fan=fan)
        semaforo.calcular_estado_final(project)
        logger_AFD.info("Semáforo actualizado %s", datetime.now())
    except Exception:
        logger_AFD.exception("Error en sistema_job")

# ---------------------------------------------------
# 3. SIMULADOR DE DATOS
# ---------------------------------------------------
from applications.getdata.simulador.utilities import (
    get_active_simulator, insert_sensor_data
)

def schedule_simulator():
    """Crea / actualiza el job del simulador según el modelo `Simulador`."""
    sim = get_active_simulator()

    try:
        scheduler.remove_job(SIMULATOR_JOB_ID)
    except Exception:
        pass

    if not sim or not sim.estado:
        logger_AFD.info("Simulador OFF: sin job programado.")
        return

    intervalo = max(1, int(sim.insert_interval))
    scheduler.add_job(
        insert_sensor_data,
        trigger=IntervalTrigger(seconds=intervalo),
        id=SIMULATOR_JOB_ID,
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=15,
    )
    logger_AFD.info("Simulador ON: inserción cada %s s", intervalo)

# ---------------------------------------------------
# 4. START-UP GENERAL
# ---------------------------------------------------
from applications.getdata.models import IntervalosDeActualizacion

def start_scheduler():
    """
    Programa sensor_job + sistema_job con los intervalos de la BD
    y reprograma el simulador según el modelo `Simulador`.
    """
    try:
        intervalos = IntervalosDeActualizacion.objects.latest("id")
    except IntervalosDeActualizacion.DoesNotExist:
        intervalos = None

    # Limpia jobs antiguos
    for job_id in (SENSOR_JOB_ID, SISTEMA_JOB_ID):
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass

    if intervalos:
        valor_sistema = getattr(intervalos, 'sistema', None) or 30 
        scheduler.add_job(
            sensor_job,
            trigger = IntervalTrigger(seconds=valor_sistema),
            id=SENSOR_JOB_ID,
            replace_existing=True,
        )
        scheduler.add_job(
            sistema_job,
            trigger=IntervalTrigger(seconds=intervalos.semaforo),
            id=SISTEMA_JOB_ID,
            replace_existing=True,
        )
        logger_AFD.info(
            "Historiadores ON: sensores=%ss, semáforo=%ss",
            intervalos.sistema,
            intervalos.semaforo,
        )
    else:
        logger_AFD.warning("Sin IntervalosDeActualizacion; historiadores OFF")

    # (Re)programa simulador
    schedule_simulator()

    # Arranca scheduler si aún no corre
    if not scheduler.running:
        scheduler.start()

    # Log de jobs activos
    for j in scheduler.get_jobs():
        logger_AFD.debug("Job %s → next %s", j.id, j.next_run_time)


def reschedule_historiadores():
    """
    Reprograma sensor_job y sistema_job con los nuevos segundos almacenados
    en IntervalosDeActualizacion.
    """
    try:
        intervalos = IntervalosDeActualizacion.objects.latest("id")
    except IntervalosDeActualizacion.DoesNotExist:
        logger_AFD.warning("No hay IntervalosDeActualizacion, no se reprograma nada.")
        return

    for job_id in (SENSOR_JOB_ID, SISTEMA_JOB_ID):
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass

    scheduler.add_job(
        sensor_job,
        trigger=IntervalTrigger(seconds=intervalos.sistema),
        id=SENSOR_JOB_ID,
        replace_existing=True,
    )
    scheduler.add_job(
        sistema_job,
        trigger=IntervalTrigger(seconds=intervalos.semaforo),
        id=SISTEMA_JOB_ID,
        replace_existing=True,
    )

    logger_AFD.info(
        "Historiadores re-programados • sensores=%ss • semáforo=%ss",
        intervalos.sistema, intervalos.semaforo,
    )