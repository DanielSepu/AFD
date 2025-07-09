from math import sqrt
import traceback
from django.shortcuts import render
import numpy as np
import pandas as pd  # Importa pandas
from django.contrib import messages

from applications.currentstatus.tools import goal_seek_custom
from applications.currentstatus.utils import caudal_aire_sensor1, velocidad_aire_sensor
from applications.fandesign.mixins import FanCalculationsMixin
from applications.fandesign.models import GraficoTolerancia
from applications.fandesign.utils import calcular_la_curva_estatica, calcular_la_curva_total, calcular_la_presion_maxima
from applications.fanreal.fanAdministrator import FanAdministrator
from modules.graphdata import *
from modules.queries import *
from django.db.models import Max
from applications.getdata.models import Proyecto
from core.logger_config import logger_AFD

from django.views.generic import TemplateView


def fandesign(request):
   if request.method == 'GET':
      try:
         # Obtener el tipo de gráfico seleccionado desde la solicitud
         chart_type = request.GET.get('chart_type')
         # Lógica para diferentes tipos de gráficos
         latest_record_sensors = SensorsData.objects.using('sensorDB').aggregate(Max('id'))
         max_id_sensors = latest_record_sensors['id__max']
         item_sensors = SensorsData.objects.using('sensorDB').get(id=max_id_sensors)
         mid_densidad = item_sensors.ps1/2
         
         #identifica id de  último proyecto guardado
         proyect =  Proyecto.objects.all().order_by('id').last() 

         df_fan = pd.DataFrame(data=dict(proyect.curva_diseno.datos_curva), dtype=float)
         df_sensor1 = get_10min_sensor_data() # desde BD

         df_vdf = get_10min_vdf_data() # desde BD

         # obtener datos
         Q_medido = df_sensor1["ps1"].mean()
         Q_medido = float(Q_medido)
         P_medido = df_sensor1["pt1"].mean()
         P_medido = float(P_medido)
         
         logger_AFD.debug(f"Q_medido: {Q_medido}  P_medido: {P_medido}")
         # indice del valor maximo de presion 
         ind  = df_fan['presion'].idxmax()
         # obtiene la ultima medicion del sensor
         ultima_medicion =  SensorsData.objects.using("sensorDB").all().order_by('-ts').first()  
         
         # calculando la densidad
         calculador_densidad_aire_s1 = calculo_densidad_aire_sensor( proyect)
         densidad2 = calculador_densidad_aire_s1.densidad_del_aire()

         presion_dinamica = item_sensors.pt1 - item_sensors.ps1
         velocidad_aire_sensor1 = velocidad_aire_sensor(presion_dinamica, calculador_densidad_aire_s1.densidad_del_aire())
         area_ducto = proyect.ducto.area
         caudal = caudal_aire_sensor1(velocidad_aire_sensor1, area_ducto)
         # presion estatica / caudal al cuadrado
         
         try:
            resistencia_actual = ultima_medicion.ps1/ caudal**2
         except AttributeError:
            resistencia_actual = 0.1
            messages.warning(request,f"Aun no hay datos del sensor")

         # Y = R * X**2
         ajuste_cubico = np.polyfit(df_fan['caudal'], df_fan['presion'], 3)

         ecuacion1, ecuacion2, goal_seek = goal_seek_custom(ajuste_cubico, resistencia_actual)
         # distancia 2 = sqrt(X**2 + ecuacion 2 **2)
         distancia2 = sqrt(goal_seek**2 + ecuacion2 **2)

         # distancia1 = sqrt(caudal**2 + presion_total**2)
         distancia1 = sqrt((Q_medido**2)+(P_medido**2))

         rotacion_actual = np.mean(df_vdf.rpm)
         # rendimiento ventilador = distancia 1 / distancia 2
         rendimiento_ventilador = round(distancia1 / distancia2, 3)

         # peak_pressure = ecuacion1 /presion maxima
         peak_pressure =  int(ecuacion1/df_fan.loc[ind]['presion'] )
         scatter_data_fan_list = []
         
         rpm_del_proyecto = proyect.curva_diseno.rpm
         densidad1 = proyect.curva_diseno.densidad
         area_difusor = 3.14159 * (proyect.ventilador.nmm/2000)**2
         rpm_model = df_vdf['rpm'].mean()

         curva_estatica_ajustada = calcular_la_curva_estatica(df_fan, rpm_model, rpm_del_proyecto, densidad2, densidad1, area_difusor)
         indice = curva_estatica_ajustada["presion"].idxmax()
         
         r_max  = curva_estatica_ajustada.loc[indice]['presion']/curva_estatica_ajustada.loc[indice]['caudal']**2
         # porcentaje de rendimiento del ventilador 
         # peak resistance = resistencia / resistencia maxima
         peak_resistance = round(resistencia_actual/r_max, 2)*100
         
         df_total_pressure  = calcular_la_curva_total(df_fan, rpm_model, rpm_del_proyecto, densidad2, densidad1 )
         indice_max = df_total_pressure["presion"].idxmax()
         
         presion_maxima = calcular_la_presion_maxima(item_sensors, df_total_pressure, indice_max)

         if chart_type == 'total_pressure':
            # creando curva inicial 

            scatter_data_fan_list_inicial = df_fan[['caudal','presion']].to_dict(orient='records')
            # datos de la curva ajustada por RPM 
            curva_ajustada_x_rpm = pd.DataFrame({'presion_ajustada': df_fan['presion'].mul((rpm_model / rpm_del_proyecto) ** 2), 'caudal_ajustado': df_fan['caudal'].mul(rpm_model / rpm_del_proyecto)})
            # datos de la curva ajustada por la densidad
            curva_ajusta_x_densidad = calcular_la_curva_total(df_fan, rpm_model, rpm_del_proyecto, densidad2, densidad1 )

            
            scatter_data_fan_list = curva_ajusta_x_densidad[['caudal','presion']].to_dict(orient='records')
            for k,v in enumerate(scatter_data_fan_list):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['PRESION (Pa)'] = v['presion']
               del v['caudal']
               del v['presion']

         elif chart_type == 'static_pressure':
            
            # creando curva inicial
            scatter_data_fan_list_inicial = df_fan[['caudal','presion']].to_dict(orient='records')

            for k,v in enumerate(scatter_data_fan_list):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['PRESION (Pa)'] = v['presion']
               del v['caudal']
               del v['presion']
            
            ### SENSORs DATA ###  #Reemplazar con datos sensor BD
            
            df_sensor1 = get_10min_sensor_data()
            ### VDF DATA ###
            df_vdf = get_10min_vdf_data() # desde BD 

            # CALCULANDO LA PRESION ESTATICA
            curva_ajusta_x_densidad = calcular_la_curva_estatica(df_fan, rpm_model, rpm_del_proyecto, densidad2, densidad1, area_difusor)
            
            
            scatter_data_fan_list = curva_ajusta_x_densidad[['caudal','presion']].to_dict(orient='records')

            for k,v in enumerate(scatter_data_fan_list):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['PRESION (Pa)'] = v['presion']
               del v['caudal']
               del v['presion']

         elif chart_type == 'power':
            
            # creando curva inicial
            scatter_data_fan_list_inicial = df_fan[['caudal','potencia']].to_dict(orient='records')
            for k,v in enumerate(scatter_data_fan_list_inicial):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['POTENCIA (kW)'] = v['potencia']
               del v['caudal']
               del v['potencia']
            
            ### SENSORs DATA ###  #Reemplazar con datos sensor BD
            #df_sensor1 = get_sensor_data()
            df_sensor1 = SensorsData.objects.using('sensorDB').all().last()
            ### VDF DATA ###
            df_vdf = get_vdf_data()
            df_vdf =  VdfData.objects.using('sensorDB').all().last()

            P_medido = df_vdf.power

            # formula para caudal: B15*($G$2/$C$2)
            # formula para potencia C15*($G$2/$C$2)^3
            curva_ajustada_x_rpm = pd.DataFrame(
               {
               'potencia_ajustada': df_fan['potencia'].mul((rpm_model / rpm_del_proyecto) **3), 
               'caudal_ajustado': df_fan['caudal'].mul((rpm_model / rpm_del_proyecto))}
               )
            
            # formula segundo ajuste: G15*($J$3/$G$3)
            curva_ajusta_x_densidad = pd.DataFrame(
                  {
                     'caudal':curva_ajustada_x_rpm['caudal_ajustado'], 
                     'potencia_ajustada': curva_ajustada_x_rpm['potencia_ajustada'].mul((densidad2/densidad1)) 
                  }
               )

            #scatter_data_fan_list = df_fan[['caudal','potencia']].to_dict(orient='records')
            scatter_data_fan_list = curva_ajusta_x_densidad[['caudal','potencia_ajustada']].to_dict(orient='records')
            for k,v in enumerate(scatter_data_fan_list):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['POTENCIA (kW)'] = v['potencia_ajustada']
               del v['caudal']
               del v['potencia_ajustada']

         else:
            return render(request, 'fanDesign.html')
         
         # Convierte los datos a una lista de diccionarios
         # Pasa los datos a la plantilla
         XY_segunda = []

         distancia_constante = Q_medido // 5
         Q_curvaR=[0]
         for i in range(1, 6):
            Q_curvaR.append(i * distancia_constante)
         Q_curvaR.append(Q_medido)# Representa X

         R=P_medido/Q_medido**2

         P_curvaR = []
         for Qi in Q_curvaR:
            P_curvaR.append(R * Qi**2)# Representa Y

         for i in range(0, 6):
            XY_segunda.append({'caudal':Q_curvaR[i],'presion':P_curvaR[i]})

         context = {
                  'scatter_data': scatter_data_fan_list, 
                  'curva_inicial': scatter_data_fan_list_inicial, 
                  'scatter_data2':XY_segunda, 
                  'chart_type': chart_type, 
                  'c':[Q_medido,P_medido], 
                  'proyecto': proyect,
                  'peak_resistance':peak_resistance,
                  'peak_pressure':peak_pressure,
                  'densidad_actual':round(densidad2,2),
                  'rendimiento_ventilador':round(rendimiento_ventilador, 1),
                  'rotacion_actual':round(rotacion_actual, 1),
                  'presion_maxima':presion_maxima,
                  'promedios': [Q_medido, P_medido]
                  }
         return render(request, 'fanDesign.html', context)
      except Exception as e:
         traceback.print_exc()
         messages.warning(request,f"Warning: {e}")

   # Si la solicitud no es un POST, simplemente renderiza la página sin datos
   return render(request, 'fanDesign.html')



TEMPLATE_NAME = 'fanDesign.html'
class FanDesignView(FanCalculationsMixin, TemplateView):
    template_name = TEMPLATE_NAME

    def get(self, request, *args, **kwargs):
        chart_type = request.GET.get('chart_type')
        context = {}
        try:
            try:
               tolerancia_obj = GraficoTolerancia.objects.get(tipo=chart_type)
               tolerancia = tolerancia_obj.tolerancia
            except GraficoTolerancia.DoesNotExist:
               tolerancia = 'AN3'

            proyecto = self.get_proyecto()
            sensor_item = self.get_latest_sensor_item()
            ultima_med = self.get_ultima_medicion()

            df_fan = pd.DataFrame(data=proyecto.curva_diseno.datos_curva, dtype=float) # type: ignore
            df_sensor1 = get_10min_sensor_data()
            df_vdf = get_10min_vdf_data()

            Q_medido, P_medido = self.compute_sensor_means(df=df_sensor1)
            
            
            logger_AFD.debug(msg=f"Q_medido: {Q_medido} P_medido: {P_medido}")
            Fan = FanAdministrator(project=proyecto)
            densidad2 = Fan.densidad_del_aire_s1()
            
            
            presion_dinamica = sensor_item.pt1 - sensor_item.ps1
            velocidad = velocidad_aire_sensor(presion_dinamica_sensor=presion_dinamica, densidad_aire_sensor1=densidad2)
            caudal = caudal_aire_sensor1(velocidad_aire_sensor1=velocidad, area_ducto=proyecto.ducto.area) # type: ignore

            resistencia = self.compute_resistencia(ultima_med=ultima_med, caudal=caudal)
            
            if resistencia is None:
                resistencia = 0.1
                messages.warning(request, "Aún no hay datos del sensor")

            ajuste = np.polyfit(df_fan['caudal'], df_fan['presion'], 3)
            ecu1, ecu2, goal_seek = goal_seek_custom(ajuste, resistencia)

            distancia2 = sqrt(goal_seek**2 + ecu2**2)
            distancia1 = sqrt(Q_medido**2 + P_medido**2)
            rendimiento = round(distancia1 / distancia2, 3)

            ind = df_fan['presion'].idxmax()
            peak_pressure = int(ecu1 / df_fan.loc[ind]['presion'])

            rpm_model = df_vdf['rpm'].mean()
            curva_est = calcular_la_curva_estatica(
                df_fan, rpm_model, proyecto.curva_diseno.rpm,
                densidad2, proyecto.curva_diseno.densidad,
                3.14159 * (proyecto.ventilador.nmm/2000)**2
            )
            idx_max = curva_est['presion'].idxmax()
            r_max = curva_est.loc[idx_max]['presion'] / curva_est.loc[idx_max]['caudal']**2
            peak_resistance = round(resistencia / r_max, 2) * 100

            df_total = calcular_la_curva_total(
                df_fan, rpm_model, proyecto.curva_diseno.rpm,
                densidad2, proyecto.curva_diseno.densidad
            )
            idx_tp = df_total['presion'].idxmax()
            presion_maxima = calcular_la_presion_maxima(sensor_item, df_total, idx_tp)

            if chart_type == 'total_pressure':
               context['curva_inicial'] = df_fan[['caudal','presion']].to_dict('records')
               context['scatter_data'] = self.build_scatter_records(
                  df_total, 'caudal', 'presion', 'caudal', 'presion'
               )
            elif chart_type == 'static_pressure':
               context['curva_inicial'] = df_fan[['caudal','presion']].to_dict('records')
               context['scatter_data'] = self.build_scatter_records(
                  curva_est, 'caudal', 'presion', 'caudal', 'presion'
               )
            elif chart_type == 'power':
               context['curva_inicial'] = df_fan[['caudal','potencia']].to_dict('records')
               adjusted = pd.DataFrame({
                  'caudal': df_fan['caudal'] * (rpm_model/proyecto.curva_diseno.rpm),
                  'potencia': df_fan['potencia'] * (rpm_model/proyecto.curva_diseno.rpm)**3 * (densidad2/proyecto.curva_diseno.densidad)
               })
               context['scatter_data'] = self.build_scatter_records(
                  adjusted, 'caudal', 'potencia', 'caudal', 'potencia'
               )

            else:
                return self.render_to_response(context)

            # Secondary curve
            R = P_medido / Q_medido**2
            Qs = [i*(Q_medido//5) for i in range(6)] + [Q_medido]
            Ys = [R * q**2 for q in Qs]
            context['scatter_data2'] = [{'caudal': Qs[i], 'presion': Ys[i]} for i in range(6)]
            
            fan = FanAdministrator(project=proyecto)
            q1 = fan.velocidad_aire_sensores['sensor1']
            logger_AFD.info(context)
            print(f"---> {fan.velocidad_aire_sensores['sensor1']}  -- {fan.caudal_aire_sensores['sensor1']}")
            context.update({
                'chart_type': chart_type,
                'c': [fan.caudal_aire_sensores['sensor1'], sensor_item.pt1],
                'proyecto': proyecto,
                'peak_resistance': peak_resistance,
                'peak_pressure': peak_pressure,
                'densidad_actual': round(densidad2,2),
                'rendimiento_ventilador': round(rendimiento,1),
                'rotacion_actual': round(rpm_model,1),
                'presion_maxima': presion_maxima,
                'tolerancia_actual': tolerancia,
                'niveles_tolerancia': ['AN1', 'AN2', 'AN3', 'AN4'],
            })
            logger_AFD.debug(context['c'])
        except Exception as e:
            import traceback; traceback.print_exc()
            messages.warning(request, f"Warning: {e}")

        return self.render_to_response(context)
  
     