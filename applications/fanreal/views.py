from django.shortcuts import render
import pandas as pd  # Importa pandas
from django.http import HttpResponse
import requests as rq

from django.conf import settings
import os

from applications.getdata.models import Proyecto, SensorsData
from modules.graphdata import dens_adjust_power, dens_adjust_pt, get_fan_data, get_sensor_data, get_vdf_data, rpm_adjust_caudal, rpm_adjust_power, rpm_adjust_pt
from modules.queries import get_10min_sensor_data, get_10min_vdf_data

def fanreal(request):
   if request.method == 'GET':
      # Obtener el tipo de gráfico seleccionado desde la solicitud
      chart_type = request.GET.get('chart_type')
      # Lógica para diferentes tipos de gráficos
      
      #identifica id de  último proyecto guardado
      #id_proyecto = Proyecto.objects.using('sensorDB').aggregate(Max('id'))['id__max']
      proyect =  Proyecto.objects.all().order_by('id').last()
      # datos insertados en curva de diseño, convertidos a dataframe
      df_fan = get_fan_data(proyect, 'pt')
      print(df_fan)
      # indice del valor maximo de presion 
      ind  = df_fan['presion'].idxmax()
      # obtener el cociente de entre presion maxima y el caudal maximo
      r_max  = df_fan.loc[ind]['presion']/df_fan.loc[ind]['caudal']
      # obtiene la ultima medicion del sensor
      ultima_medicion =  SensorsData.objects.all().order_by('id').last()  
      # presion estatica / caudal al cuadrado
      r_actual = ultima_medicion.ps1/ ultima_medicion.q1**2
      # porcentaje de rendimiento del ventilador 
      pr = int(r_max/r_actual *100)
      peak_pressure =  int(ultima_medicion.ps1/df_fan.loc[ind]['presion'] *100 )
      scatter_data_fan_list = []
      if chart_type == 'total_pressure':
      
         ### SENSORs DATA ###
         # df_sensor1 = get_sensor_data() # desde CSVs

         df_sensor1 = get_10min_sensor_data() # desde BD
         ### VDF DATA ###

         # df_vdf = get_vdf_data() # desde CSVs
         df_vdf = get_10min_vdf_data() # desde BD
         Q_medido = df_sensor1["q1"].mean()
         P_medido = df_sensor1["pt1"].mean()
         densidad_fan = float(proyect.curva_diseno.densidad) 
         densidad_sensor1 = df_sensor1["densidad1"].mean()
         #print(df_sensor1)
         rpm_fan = float(proyect.curva_diseno.rpm)
         rpm_vdf = df_vdf["rpm"].mean()
      
         df_adjust = pd.DataFrame()
         df_adjust['q_rpm']=rpm_adjust_caudal(df_fan['caudal'],rpm_fan,rpm_vdf)
         df_adjust['pt_rpm']=rpm_adjust_pt(df_fan['presion'],rpm_fan,rpm_vdf)
         df_adjust['pt_dens']=dens_adjust_pt(df_adjust['pt_rpm'],densidad_fan,densidad_sensor1)

         df_graph = df_adjust.loc[:, ["q_rpm", "pt_dens"]]
         scatter_data_fan_list = df_fan[['caudal','presion']].to_dict(orient='records')
         print(f"scater data")
         print(scatter_data_fan_list)

         for k,v in enumerate(scatter_data_fan_list):
            v['CAUDAL(m3/s)'] = v['caudal']
            v['PRESION(Pa)'] = v['presion']
            del v['caudal']
            del v['presion']

      elif chart_type == 'static_pressure':
      
         ### SENSORs DATA ###  #Reemplazar con datos sensor BD
         df_sensor1 = get_sensor_data()
         ### VDF DATA ###
         df_vdf = get_vdf_data()

         Q_medido = df_sensor1["q1"].mean()
         P_medido = df_sensor1["pe1"].mean()
         densidad_fan = float(proyect.curva_diseno.densidad)
         densidad_sensor1 = df_sensor1["densidad1"].mean()
         rpm_fan = float(proyect.curva_diseno.rpm)
         rpm_vdf = df_vdf["rpm"].mean()
      
         df_adjust = pd.DataFrame()
         df_adjust['q_rpm']=rpm_adjust_caudal(df_fan['caudal'],rpm_fan,rpm_vdf)
         df_adjust['pt_rpm']=rpm_adjust_pt(df_fan['presion'],rpm_fan,rpm_vdf)
         df_adjust['pt_dens']=dens_adjust_pt(df_adjust['pt_rpm'],densidad_fan,densidad_sensor1)

         df_graph = df_adjust.loc[:, ["q_rpm", "pt_dens"]]
         scatter_data_fan_list = df_fan[['caudal','presion']].to_dict(orient='records')

         for k,v in enumerate(scatter_data_fan_list):
            v['CAUDAL(m3/s)'] = v['caudal']
            v['PRESION(Pa)'] = v['presion']
            del v['caudal']
            del v['presion']

      elif chart_type == 'power':
         
         ### SENSORs DATA ###  #Reemplazar con datos sensor BD
         df_sensor1 = get_sensor_data()
         ### VDF DATA ###
         df_vdf = get_vdf_data()

         Q_medido = df_sensor1["q1"].mean()
         P_medido = df_vdf["potencia"].mean()  

         densidad_fan = proyect.curva_diseno.densidad
         densidad_sensor1 = df_sensor1["densidad1"].mean()
         rpm_fan = proyect.curva_diseno.rpm
         rpm_vdf = df_vdf["rpm"].mean()

         df_adjust = pd.DataFrame()
         df_adjust['q_rpm']=rpm_adjust_caudal(df_fan['caudal'],rpm_fan,rpm_vdf)
         df_adjust['power_rpm']=rpm_adjust_power(df_fan['potencia'],rpm_fan,rpm_vdf)
         df_adjust['power_dens']=dens_adjust_power(df_adjust['power_rpm'],densidad_fan,densidad_sensor1)
            
         df_graph = df_adjust.loc[:, ["q_rpm", "power_dens"]]
         scatter_data_fan_list = df_fan[['caudal','potencia']].to_dict(orient='records')
         
         for k,v in enumerate(scatter_data_fan_list):
            v['CAUDAL(m3/s)'] = v['caudal']
            v['POTENCIA(kW)'] = v['potencia']
            del v['caudal']
            del v['potencia']

      else:
         return render(request, 'fanReal.html')
      

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

      context = {'scatter_data': scatter_data_fan_list, 'scatter_data2':XY_segunda, 'chart_type': chart_type, 'c':[Q_medido,P_medido], 'proyecto':proyect , 'peak_resistance':pr, 'peak_pressure':peak_pressure }
      # print(f"context: {context}")
      return render(request, 'fanReal.html', context)

   # Si la solicitud no es un POST, simplemente renderiza la página sin datos
   return render(request, 'fanReal.html')