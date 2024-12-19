


import pandas as pd
from modules.graphdata import dens_adjust_pt, get_fan_data, rpm_adjust_caudal, rpm_adjust_pt


def presion_total(proyecto, df_vdf, df_sensor):
    """_summary_

    Args:
        proyecto (model): proyecto actual - ultimo proyecto
        df_vdf (model): datos del sensor ultimo registro
        df_sensor (_type_): _description_
    """
    rpm_fan = float(proyecto.curva_diseno.rpm)
    rpm_vdf = df_vdf["rpm"].mean()
    densidad_fan = float(proyecto.curva_diseno.densidad) 
    densidad_sensor1 = df_sensor["densidad1"].mean()
    df_fan = get_fan_data(proyecto, 'pt')
    
    #  Definición del DataFrame vacío y declaración de las columnas
    df_adjust = pd.DataFrame({
        'q_rpm': rpm_adjust_caudal(df_fan['caudal'], rpm_fan, rpm_vdf),
        'pt_rpm': rpm_adjust_pt(df_fan['presion'], rpm_fan, rpm_vdf),
        'pt_dens': pd.NA,
    })
    
    # Ajuste de densidad basado en los valores calculados de 'pt_rpm'
    df_adjust['pt_dens'] = dens_adjust_pt(df_adjust['pt_rpm'], densidad_fan, densidad_sensor1)

    # Creación del DataFrame para el gráfico
    df_graph = df_adjust.loc[:, ["q_rpm", "pt_dens"]].rename(columns={"q_rpm": "caudal", "pt_dens": "presion"})

    return df_graph


def presion_total_2(N, mid_densidad, Q):
    # Area difusor = 3.14159*(N(mm)/2000)^2
    # Presión total - mid_densidad*((Q^2)/(Adifusor^2))
    area_difusor = 3.14159 * (N/2000)**2
    return mid_densidad*((Q**2)/area_difusor)