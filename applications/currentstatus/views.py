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
from applications.currentstatus.utils import calculo_densidad_aire_sensor, caudal_aire_sensor1, caudal_de_la_frente, presion_dinamica_sensor_1, velocidad_aire_sensor
from applications.getdata.models import Proyecto, SensorsData, VdfData
from django.db.models import Max
from applications.getdata.simulador.simulador import insert_sensor_data
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
        # insert_sensor_data()
        # VARIABLES DEL SENSOR 
        latest_record_sensors = SensorsData.objects.using('sensorDB').aggregate(Max('id'))
        max_id_sensors = latest_record_sensors['id__max']
        item_sensors = SensorsData.objects.using('sensorDB').get(id=max_id_sensors)
        variables = {}
        
        # FUNCION DEL SIMULADOR PARA INSERTAR NUEVOS DATOS CADA VEZ QUE SE LLAMA ESTA FUNCION
        # ()
        latest_record_vdf = VdfData.objects.using('sensorDB').aggregate(Max('id'))
        max_id_vdf = latest_record_vdf['id__max']

        # calcular la perdida por choque
        project = Proyecto.objects.all().order_by('id').last() 
        caracteristicas = project.ventilador.accesorios.all()

        variables['vmm'] = project.ventilador.vmm
        variables['amm'] = project.ventilador.amm
        variables['nmm'] = project.ventilador.nmm
        
        item_vdf = VdfData.objects.using('sensorDB').get(id=max_id_vdf)
        
        # densidad configurada en el proyecto
        variables['densidad'] = item_sensors.ps1
        
        # densidad calculada
        calculador_densidad_aire_s1 = calculo_densidad_aire_sensor(project)
        densidad = calculador_densidad_aire_s1.densidad_del_aire()

        mid_densidad = densidad/2
        # CONFIGURAR EL SEMAFORO PARA OBTENER CAUDALES
        semaforo = Semaforo()
        semaforo.encender(project)
        caudal_del_ventilador = semaforo.calculate_Q1()
        Qf = caudal_de_la_frente(semaforo.calculate_Q2(), semaforo.leakage_coefficient_v4(), item_sensors.pt2, project.ducto.Ldsf )
        
        # cambio de valores 
        variables ['caudal_del_ventilador'] = caudal_del_ventilador
        
        Q_codo_1 = caudal_del_ventilador**2
        area_inlet_bell_val = area_inlet_bell(project)
        Area_ventilador = 3.14159 * (project.ventilador.amm/2000)**2
        variables['area_inlet_bell_val']  = area_inlet_bell_val
        variables['Area_ventilador']  = Area_ventilador
        
        presion_dinamica_entrada_Pa = mid_densidad * Q_codo_1 / (area_inlet_bell_val*area_inlet_bell_val)
  
        variables['presion_dinamica_entrada_Pa'] = presion_dinamica_entrada_Pa

        Presion_dinamica_ventilador_Pa = mid_densidad * Q_codo_1 / (Area_ventilador*Area_ventilador)
        variables['Presion_dinamica_ventilador_Pa'] = Presion_dinamica_ventilador_Pa
        '''
           La perdida de choque de accesorios es la presion de choque de accesorios por la presion dinamica
        '''
        sumatoria_choque_accesorios = 0
        for caracteristica in caracteristicas:
            sumatoria_choque_accesorios += caracteristica.factor_choque*presion_dinamica_entrada_Pa

        # calcular perdida por choque de los codos
        total_codos = project.codos
        variables['sumatoria_choque_accesorios'] = sumatoria_choque_accesorios

        try:
            vars, perdidas_choque_codos = calculate_perdida_choque_codos(
                        total_codos=total_codos, 
                        mid_densidad=mid_densidad, 
                        Q1=caudal_del_ventilador,
                        project=project, 
                        Qf = Qf
                        )
            variables["perdida_choque_codos"] = perdidas_choque_codos

        except TypeError as e:
            traceback.print_exc()
            context = {}
            context["status"] = "error"
            context["message"] = f"No se pudo realizar el calculo de calcular choque de codos: {e}, verifique el valor de diametro del ducto"
            return JsonResponse(context, safe=False)

        try:
            area_ducto_circular_ = area_ducto_circular(project)
        except TypeError as e:
            context = {}
            context["status"] = "error"
            context["message"] = f"No se pudo realizar el calculo: {e}, verifique el valor de diametro del ducto"

            return JsonResponse(context, safe=False)

        perdida_choque_salida_ducto_circular = mid_densidad*(Qf*Qf/(area_ducto_circular_*area_ducto_circular_))
        perdida_choque_salida_ducto_ovalado = mid_densidad*Qf*Qf/(project.ducto.area*project.ducto.area)

        perdida_choque_salida_ducto = None 
        if project.ducto.t_ducto == "ovalado":
            perdida_choque_salida_ducto = perdida_choque_salida_ducto_ovalado
        elif project.ducto.t_ducto == "circular":
            perdida_choque_salida_ducto = perdida_choque_salida_ducto_circular
        
        if perdida_choque_salida_ducto is None:
            raise ValueError("No se pudo identificar el tipo de ducto")

        variables['perdida_choque_salida_ducto'] = perdida_choque_salida_ducto
        variables['perdida_choque_salida_ducto2'] = perdida_choque_salida_ducto
        #a -> resistencia
        presion_total = item_sensors.pt1 
        presion_estatica_ventilador = round(presion_total - presion_dinamica_entrada_Pa, 0)
        # este calculo obtiene el valor  adecuado independientemente del tipo de ducto, es decir funciona para circular y ovalado
        perdida_choque_total_sistema_ducto = perdidas_choque_codos +sumatoria_choque_accesorios+perdida_choque_salida_ducto
        
        variables['perdida_choque_total_sistema_ducto'] = perdida_choque_total_sistema_ducto
       
        presion_dinamica = item_sensors.pt1 - item_sensors.ps1
        
        var_intermedia = presion_total - presion_dinamica
        
        perdidas_friccionales = var_intermedia - perdida_choque_total_sistema_ducto
        # calculando el caudal del aire sensor 1
        velocidad_aire_sensor1 = velocidad_aire_sensor(presion_dinamica, calculador_densidad_aire_s1.densidad_del_aire())
        area_ducto = project.ducto.area
        data = {
            "pt1": round(item_sensors.pt1, 2),
            "qf": round(item_sensors.HRs1, 2),
            "q1": caudal_aire_sensor1(velocidad_aire_sensor1, area_ducto),
            "HRs2": round(item_sensors.HRs2, 2),
            "densidad1": round(item_sensors.ps1, 2),
            "powerc": round(item_vdf.powerc, 2),
            "fref": round(item_vdf.fref, 2),
            "frequency_ratio_1": round((item_vdf.freal / item_vdf.fref) * 100, 2),
            "frequency_ratio_2": round((item_vdf.freal / item_vdf.fref) * 100, 2),
            "powerc_duplicate": round(item_vdf.powerc, 2),
        }
        
        context = {}
        context["data"] = data
       
        context["presion_estatica"] = round(presion_estatica_ventilador, 1)
        context["presion_dinamica"] = round(presion_dinamica, 1)
        context["perdida_de_choque"] = round(perdida_choque_total_sistema_ducto, 0)
        context["perdidas_friccionales"] = round(perdidas_friccionales, 0)
        context['variables'] = variables
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
    