from math import sqrt
import pdb
import traceback
from django.shortcuts import render
import numpy as np
import pandas as pd  # Importa pandas
from django.contrib import messages

from applications.currentstatus.tools import goal_seek_custom
from applications.fandesign.mixins import presion_total, presion_total_2
from modules.graphdata import *
from modules.queries import *
from django.db.models import Max
from applications.getdata.models import Proyecto

# Constants
rpm_del_proyecto = 3000
rpm_model = 3000

def fandesign(request):
   if request.method == 'GET':
      try:
         # Obtener el tipo de gráfico seleccionado desde la solicitud
         chart_type = request.GET.get('chart_type')
         # Lógica para diferentes tipos de gráficos
         latest_record_sensors = SensorsData.objects.using('sensorDB').aggregate(Max('id'))
         max_id_sensors = latest_record_sensors['id__max']
         item_sensors = SensorsData.objects.using('sensorDB').get(id=max_id_sensors)
         mid_densidad = item_sensors.densidad1/2
         
         #identifica id de  último proyecto guardado
         #id_proyecto = Proyecto.objects.using('sensorDB').aggregate(Max('id'))['id__max']
         proyect =  Proyecto.objects.all().order_by('id').last()

         df_fan = pd.DataFrame(dict(proyect.curva_diseno.datos_curva)).astype(float)
         df_fan = df_fan.copy()  # Evita problemas con referencias internas
         rpm_del_proyecto = 3000
         rpm_model = 3000
         df_fan['p_ajustada_rpm'] = df_fan['presion'] * (rpm_model / rpm_del_proyecto) ** 2


         
         df_sensor1 = get_10min_sensor_data() # desde BD
         #df_sensor1 = SensorsData.objects.using('sensorDB').all().last()
         ### VDF DATA ###
         # df_vdf = get_vdf_data() # desde CSVs
         df_vdf = get_10min_vdf_data() # desde BD

         # obtener datos
         Q_medido = df_sensor1["q1"].mean()
         Q_medido = float(Q_medido)
         P_medido = df_sensor1["pt1"].mean()
         P_medido = float(P_medido)
         
         # indice del valor maximo de presion 
         ind  = df_fan['presion'].idxmax()

         # obtiene la ultima medicion del sensor
         ultima_medicion =  SensorsData.objects.all().order_by('id').last()  

         # presion estatica / caudal al cuadrado
         try:
            r_actual = ultima_medicion.ps1/ ultima_medicion.q1**2
         except AttributeError:
            r_actual = 0.1
            messages.warning(request,f"Aun no hay datos del sensor")

         # Y = R * X**2
         ajuste_cubico = np.polyfit(df_fan['caudal'], df_fan['presion'], 3)
         #print(f"ajuste cubico: {ajuste_cubico}")
         # obtener el cociente de entre presion maxima y el caudal maximo
         # resistencia_maxima = presionMaxima/(caudalMaximo**2)
         r_max  = df_fan.loc[ind]['presion']/df_fan.loc[ind]['caudal']**2

         # porcentaje de rendimiento del ventilador 
         # peak resistance = resistencia / resistencia maxima
         peak_resistance = round(r_actual/r_max, 2 )

         ecuacion1, ecuacion2, goal_seek = goal_seek_custom(ajuste_cubico, r_actual)
         # distancia 2 = sqrt(X**2 + ecuacion 2 **2)
         distancia2 = sqrt(goal_seek**2 + ecuacion2 **2)

         # distancia1 = sqrt(caudal**2 + presion_total**2)
         distancia1 = sqrt((Q_medido**2)+(P_medido**2))

         rotacion_actual = np.mean(df_vdf.fref)
         print(rotacion_actual)
         # rendimiento ventilador = distancia 1 / distancia 2
         rendimiento_ventilador = round(distancia1 / distancia2, 3)

         # peak_pressure = ecuacion1 /presion maxima
         peak_pressure =  int(ecuacion1/df_fan.loc[ind]['presion'] )
         scatter_data_fan_list = []

         resistencia_del_sistema = 0
         df_graph = presion_total(proyect, df_vdf, df_sensor1)
         if chart_type == 'total_pressure':
            rpm_del_proyecto = 3000
            rpm_model = 3000
            
            new_df = pd.DataFrame({'rpm_ajustado': [rpm_adjusted]})
            df = pd.concat([df_fan, new_df], axis=1)
            print(df_fan)
            densidad_fan = float(proyect.curva_diseno.densidad) 
            densidad_sensor1 = df_sensor1["densidad1"].mean()

            presion_maxima_curvaAjustada = df_graph['presion'].max()
            fila = df_graph.loc[df_graph['presion'] == presion_maxima_curvaAjustada ]

            try:
               ps_curvaAjustada = fila.loc[0, "presion"]
            except KeyError as e:
               messages.warning(request, f"no se ha podido obtener los valores relacionados a la presión:{e}, la curva no se ha calculado, verifique los valores de diseño")
               return render(request, 'fanDesign.html') 

            ps_caudal_curvaAjustada = fila.loc[0, "caudal"]
            
            resistencia_del_sistema = (ps_curvaAjustada / ps_caudal_curvaAjustada**2)/100


            scatter_data_fan_list = df_graph[['caudal','presion']].to_dict(orient='records')
            for k,v in enumerate(scatter_data_fan_list):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['PRESION (Pa)'] = v['presion']
               del v['caudal']
               del v['presion']

         elif chart_type == 'static_pressure':
         
            ### SENSORs DATA ###  #Reemplazar con datos sensor BD
            area_difusor = 3.14159 * (proyect.ventilador.nmm/2000)**2
            df_sensor1 = get_10min_sensor_data()
            ### VDF DATA ###
            df_vdf = get_10min_vdf_data() # desde BD 
            print(f"contenido de df_grap")
            print(df_graph)
            print(df_fan)
            new_df = pd.DataFrame({
               'caudal': df_graph['caudal'],
               'presion_total': presion_total_2(proyect.ventilador.nmm, mid_densidad, df_graph['caudal']),
               'presion': df_graph['presion'],
               'potencia': df_fan['potencia'],
               'presion_estatica': calculate_presion_estatica(df_graph['presion'],mid_densidad, df_graph['caudal'], area_difusor)
            })
            
            print(new_df)
            scatter_data_fan_list = new_df[['caudal','presion_estatica']].to_dict(orient='records')

            for k,v in enumerate(scatter_data_fan_list):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['PRESION (Pa)'] = v['presion_estatica']
               del v['caudal']
               del v['presion_estatica']

         elif chart_type == 'power':
            
            ### SENSORs DATA ###  #Reemplazar con datos sensor BD
            #df_sensor1 = get_sensor_data()
            df_sensor1 = SensorsData.objects.using('sensorDB').all().last()
            ### VDF DATA ###
            df_vdf = get_vdf_data()
            df_vdf =  VdfData.objects.using('sensorDB').all().last()

            P_medido = df_vdf.power

            densidad_fan = proyect.curva_diseno.densidad
            densidad_sensor1 = df_sensor1.densidad1
            rpm_fan = proyect.curva_diseno.rpm
            rpm_vdf = df_vdf.rpm

            # Calcular las columnas necesarias y asignarlas al DataFrame df_adjust
            df_adjust = pd.DataFrame({
               'q_rpm': rpm_adjust_caudal(df_fan['caudal'], rpm_fan, rpm_vdf),
               'power_rpm': rpm_adjust_power(df_fan['potencia'], rpm_fan, rpm_vdf),
            })

            # Calcular la columna 'power_dens' utilizando las columnas previamente calculadas
            # df_adjust['power_dens'] = dens_adjust_power(df_adjust['power_rpm'], densidad_fan, densidad_sensor1)
            new_df = pd.DataFrame({
               'q_rpm': df_adjust['q_rpm'],
               'power_rpm': df_adjust['power_rpm'],
               'power_dens': dens_adjust_power(df_adjust['power_rpm'], densidad_fan, densidad_sensor1)
            })
            df_graph = new_df.loc[:, ["q_rpm", "power_dens"]]

            df_graph.rename(columns={"q_rpm":"caudal","power_dens":"potencia"}, inplace=True)

            #scatter_data_fan_list = df_fan[['caudal','potencia']].to_dict(orient='records')
            scatter_data_fan_list = df_graph[['caudal','potencia']].to_dict(orient='records')
            for k,v in enumerate(scatter_data_fan_list):
               v['CAUDAL (m³/s)'] = v['caudal']
               v['POTENCIA (kW)'] = v['potencia']
               del v['caudal']
               del v['potencia']

         else:
            return render(request, 'fanDesign.html')
         
         # Convierte los datos a una lista de diccionarios
         # print(scatter_data_fan_list)
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
                  'scatter_data2':XY_segunda, 
                  'chart_type': chart_type, 
                  'c':[Q_medido,P_medido], 
                  'proyecto':proyect , 
                  'peak_resistance':peak_resistance, 
                  'peak_pressure':peak_pressure, 
                  'rendimiento_ventilador':round(rendimiento_ventilador, 1),
                  'rotacion_actual':round(rotacion_actual, 1),

                  }
         # print(f"context: {context}")
         return render(request, 'fanDesign.html', context)
      except Exception as e:
         traceback.print_exc()
         print(f"error")
         messages.warning(request,f"Warning: {e}")

   # Si la solicitud no es un POST, simplemente renderiza la página sin datos
   return render(request, 'fanDesign.html')

