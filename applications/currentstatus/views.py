import datetime
import io
import os
import subprocess
from time import timezone
import traceback
import zipfile
from django.shortcuts import render
from django.views import View
import openpyxl
import pandas as pd  # Importa pandas
from django.http import HttpResponse, JsonResponse
import requests as rq
from django.conf import settings
from applications.currentstatus.mixin import procesar_datos_sensores
from applications.currentstatus.tools import area_ducto_circular, area_inlet_bell, calculate_perdida_choque_codos
from applications.currentstatus.utils import caudal_aire_sensor1, caudal_de_la_frente, velocidad_aire_sensor
from applications.fanreal.fanAdministrator import FanAdministrator
from applications.getdata.models import Proyecto, SensorsData, VdfData
from django.db.models import Max
from core.logger_config import logger_AFD
from modules.semaforo import Semaforo
from django.utils import timezone


class DataCurrentStatusView:
    
    def __init__(self):
        #  Inicializa las propiedades como diccionarios vacíos
        self.general = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
        self.total_pressure = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
        self.static_pressure = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
        self.power = {'FanPerformance': {'status':'' , 'data': []}, 'FanOperation': {'status':'' , 'data': []}}
    
    def add_measurement(self, property_name, fan_type, status, measurement):

        # Añade una medida a la propiedad correspondiente
        if property_name in ['general', 'total_pressure', 'static_pressure', 'power']:
            if fan_type in ['FanPerformance', 'FanOperation']:
                getattr(self, property_name)[fan_type]['data']= measurement
                getattr(self, property_name)[fan_type]['status'] = status
            else:
               pass
        else:
            pass
    
    def to_dict(self):
        # Retorna un diccionario con todas las propiedades
        return {
            'general': self.general,
            'total_pressure': self.total_pressure,
            'static_pressure': self.static_pressure,
            'power': self.power
        }
   

def currentstatus(request):
    
    if request.method == 'GET':
        csv_file_path = os.path.join(settings.MEDIA_ROOT, 'datos.csv')
        df = pd.read_csv(csv_file_path)
        context = {}
        context['project'] = Proyecto.objects.all().last()
        # Ejemplo de uso
        data_view = DataCurrentStatusView()

        # Añadiendo medidas
        data_view.add_measurement('general', 'FanPerformance','green',df[["q1", "pt1"]].to_dict(orient='records') )
        data_view.add_measurement('general', 'FanOperation','yellow', df[["q1", "pt1"]].to_dict(orient='records') )

        data_view.add_measurement('total_pressure', 'FanPerformance','red', df[["q1", "pt1"]].to_dict(orient='records'))
        data_view.add_measurement('total_pressure', 'FanOperation', 'yellow',  df[["q1", "pt1"]].to_dict(orient='records') )

        data_view.add_measurement('static_pressure', 'FanPerformance','red',  df[["q1", "pt1"]].to_dict(orient='records'))
        data_view.add_measurement('static_pressure', 'FanOperation','green',  df[["q1", "pt1"]].to_dict(orient='records'))

        data_view.add_measurement('power', 'FanPerformance','red', df[["q1", "pt1"]].to_dict(orient='records'))
        data_view.add_measurement('power', 'FanOperation', 'yellow', df[["q1", "pt1"]].to_dict(orient='records'))

        context['data']=data_view.to_dict()
        return render(request, 'currentStatus.html', context)
    
    # Si la solicitud no es un POST, simplemente renderiza la página sin datos
    return render(request, 'currentStatus.html')


def get_recent_data(request):
    '''

    '''
    if request.method == 'GET':
        
        context = procesar_datos_sensores()
        return JsonResponse(context, safe=False)
    
def update_frequency(request):
   if request.method == 'GET':
      newFref = request.GET.get('frecuency')
      url = f"http://localhost:1880/update-frequency?frecuency={newFref}"
      try:
            #Enviar al endpoint del Node-Red
            response = rq.get(url)
      except rq.exceptions.RequestException as e:
            pass

   return JsonResponse('Frecuencia Ref Actualizada', safe=False)


class ExcelDownloadView(View):
    def get(self, request, *args, **kwargs):
        # Obtener parámetros GET "inicio" y "fin"
        logger_AFD.debug("descargando documento excel")
        inicio_str = request.GET.get('inicio')
        fin_str = request.GET.get('fin')

        if inicio_str and fin_str:
            try:
                # Convertir las cadenas a objetos datetime (formato: YYYY-MM-DD)
                inicio = datetime.datetime.strptime(inicio_str, '%Y-%m-%d')
                # Incrementar un día a la fecha fin para incluirla completamente
                fin = datetime.datetime.strptime(fin_str, '%Y-%m-%d') + datetime.timedelta(days=1)
            except ValueError:
                # En caso de error, se establece un rango por defecto (últimas 24 horas)
                inicio = timezone.now() - datetime.timedelta(days=1)
                fin = timezone.now()
        else:
            # Valor por defecto si no se reciben parámetros
            inicio = timezone.now() - datetime.timedelta(days=1)
            fin = timezone.now()

        # Crear un timestamp para el nombre del archivo
        timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Datos_{timestamp}.xlsx"'

        # Crear libro de trabajo Excel
        workbook = openpyxl.Workbook()

        ## Hoja "VDF"
        worksheet = workbook.active
        worksheet.title = 'VDF'

        # Escribir cabecera
        header = ['Frecuencia referencia', 'Frecuencia Real', 'VF', 'IF', 'power', 'powerc', 'rpm']
        for col_num, column_title in enumerate(header, 1):
            worksheet.cell(row=1, column=col_num, value=column_title)

        # Consultar y escribir datos en la hoja VDF filtrados por fecha
        queryset = VdfData.objects.using('sensorDB').filter(ts__gte=inicio, ts__lt=fin).values_list('fref', 'freal', 'vf', 'oc', 'power', 'powerc', 'rpm')

        for row_num, row in enumerate(queryset, 1):
            for col_num, cell_value in enumerate(row, 1):
                worksheet.cell(row=row_num+1, column=col_num, value=cell_value)

        ## Hoja "Sensores"
        workbook.create_sheet('Sensores')
        workbook.active = workbook['Sensores']
        worksheet = workbook.active

        # Escribir cabecera para la hoja "Sensores"
        header = ['pt2', 'ps2', 'Pbs2', 'Tbs2', 'HRs2', 'pt1', 'ps1', 'Pbs1', 'Tbs1', 'HRs1', 'k']
        for col_num, column_title in enumerate(header, 1):
            worksheet.cell(row=1, column=col_num, value=column_title)

        # Consultar y escribir datos en la hoja "Sensores" filtrados por fecha
        queryset = SensorsData.objects.using('sensorDB').filter(ts__gte=inicio, ts__lt=fin).values_list('pt2', 'ps2', 'Pbs2', 'Tbs2', 'HRs2', 'pt1', 'ps1', 'Pbs1', 'Tbs1', 'HRs1', 'k')

        for row_num, row in enumerate(queryset, 1):
            for col_num, cell_value in enumerate(row, 1):
                worksheet.cell(row=row_num+1, column=col_num, value=cell_value)

        # Guardar el workbook en el objeto response
        workbook.save(response)
        return response

class BackupDownloadView(View):
    def get(self, request, *args, **kwargs):
        logger_AFD.debug("Iniciando generación del backup de las bases de datos")
        timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Creamos un buffer en memoria para el archivo ZIP
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Iteramos sobre las bases de datos definidas en settings.DATABASES
            for db_alias, db_config in settings.DATABASES.items():
                engine = db_config.get("ENGINE", "")
                backup_content = b""
                filename = f"backup_{db_alias}_{timestamp}.sql"
                
                if "postgresql" in engine:
                    # Configuración para PostgreSQL
                    host = db_config.get("HOST", "localhost")
                    port = db_config.get("PORT", 5432)
                    user = db_config.get("USER", "")
                    password = db_config.get("PASSWORD", "")
                    name = db_config.get("NAME", "")
                    
                    # Construir el comando pg_dump
                    cmd = [
                        "pg_dump",
                        "-h", host,
                        "-p", str(port),
                        "-U", user,
                        "-d", name
                    ]
                    # Copiamos el entorno y asignamos la contraseña
                    env = os.environ.copy()
                    env["PGPASSWORD"] = password
                    logger_AFD.debug(f"Ejecutando pg_dump para la base de datos '{db_alias}' con el comando: {' '.join(cmd)}")
                    
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                    if result.returncode != 0:
                        error_message = result.stderr.decode("utf-8")
                        logger_AFD.error(f"Error en pg_dump para {db_alias}: {error_message}")
                        backup_content = f"-- Error al generar backup para {db_alias}:\n{error_message}\n".encode("utf-8")
                    else:
                        backup_content = result.stdout
                        
                elif "mysql" in engine:
                    # Configuración para MySQL
                    host = db_config.get("HOST", "localhost")
                    port = db_config.get("PORT", 3306)
                    user = db_config.get("USER", "")
                    password = db_config.get("PASSWORD", "")
                    name = db_config.get("NAME", "")
                    
                    # Nota: En mysqldump, para evitar problemas con el formato de la contraseña,
                    # es recomendable pasarla directamente en el comando o definir la variable de entorno MYSQL_PWD.
                    cmd = [
                        "mysqldump",
                        "-h", host,
                        "-P", str(port),
                        "-u", user,
                        f"--password={password}",
                        name
                    ]
                    logger_AFD.debug(f"Ejecutando mysqldump para la base de datos '{db_alias}' con el comando: {' '.join(cmd)}")
                    
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if result.returncode != 0:
                        error_message = result.stderr.decode("utf-8")
                        logger_AFD.error(f"Error en mysqldump para {db_alias}: {error_message}")
                        backup_content = f"-- Error al generar backup para {db_alias}:\n{error_message}\n".encode("utf-8")
                    else:
                        backup_content = result.stdout
                        
                else:
                    # Para otros motores, se simula la generación del backup
                    backup_content = (
                        f"-- SQL Backup para la base de datos: {db_alias}\n"
                        f"-- Generado el {timestamp}\n"
                        f"-- No se implementó un backup real para el motor: {engine}\n"
                    ).encode("utf-8")
                    logger_AFD.warning(f"Se simula el backup para {db_alias} con motor {engine}")
                
                # Escribir el contenido de backup en el archivo del ZIP
                zip_file.writestr(filename, backup_content)
                logger_AFD.debug(f"Backup generado para la base de datos '{db_alias}' guardado en '{filename}'")
        
        # Preparamos la respuesta con el ZIP
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="backup_{timestamp}.zip"'
        logger_AFD.debug("Backup ZIP preparado para descarga")
        return response   
    