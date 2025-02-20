import pandas as pd


def calcular_la_curva_estatica(df_fan, rpm_model, rpm_del_proyecto, densidad2, densidad1, area_difusor):
    presion_estatica = pd.DataFrame({
               "caudal": df_fan['caudal'], 
               "presion_estatica": df_fan['presion']-(0.6*(df_fan['caudal']/area_difusor)**2)
            })
            
    curva_ajustada_x_rpm = pd.DataFrame({'presion_ajustada': presion_estatica['presion_estatica'].mul((rpm_model / rpm_del_proyecto) ** 2), 'caudal_ajustado': presion_estatica['caudal'].mul(rpm_model / rpm_del_proyecto)})
    return pd.DataFrame({'caudal':curva_ajustada_x_rpm['caudal_ajustado'], 'presion': curva_ajustada_x_rpm['presion_ajustada'].mul((densidad2/densidad1)) })



def calcular_la_curva_total(df_fan, rpm_model, rpm_del_proyecto, densidad2, densidad1 ):
    # datos de la curva ajustada por RPM 
    curva_ajustada_x_rpm = pd.DataFrame({'presion_ajustada': df_fan['presion'].mul((rpm_model / rpm_del_proyecto) ** 2), 'caudal_ajustado': df_fan['caudal'].mul(rpm_model / rpm_del_proyecto)})
    # datos de la curva ajustada por la densidad
    return pd.DataFrame({'caudal':curva_ajustada_x_rpm['caudal_ajustado'], 'presion': curva_ajustada_x_rpm['presion_ajustada'].mul((densidad2/densidad1)) })


def calcular_la_presion_maxima(item_sensors, df_total_pressure, indice_max):
    return round((item_sensors.pt1/df_total_pressure.loc[indice_max]["presion"])*100,1)