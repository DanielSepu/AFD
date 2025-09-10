


import pandas as pd
from applications.getdata.models import Proyecto, SensorsData
from django.db.models import Max
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
    densidad_sensor1 = df_sensor["ps1"].mean()
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

# Global defaults
db_alias = 'sensorDB'

class SensorDataMixin:
    db_alias = db_alias

    def get_latest_sensor_item(self):
        max_id = SensorsData.objects.using(self.db_alias).aggregate(Max('id'))['id__max']
        return SensorsData.objects.using(self.db_alias).get(id=max_id)

    def get_ultima_medicion(self):
        return SensorsData.objects.using(self.db_alias).order_by('-ts').first()

class ProjectMixin:
    def get_proyecto(self):
        return Proyecto.objects.order_by('id').last()

class FanCalculationsMixin(SensorDataMixin, ProjectMixin):
    def compute_mid_density(self, sensor_item):
        return sensor_item.ps1 / 2

    def compute_sensor_means(self, df):
        
        Q = float(df['ps1'].mean())
        P = float(df['pt1'].mean())
        return Q, P

    def compute_resistencia(self, ultima_med, caudal):
        print(f"ultima_med.ps1: {ultima_med.ps1}   -- caudal: {caudal}")
        try:
            return ultima_med.ps1 / caudal**2
        except AttributeError:
            return None
        except ZeroDivisionError:
            raise ValueError("el caudal ha caido a cero y no se puede calcular la resistencia.")

    def build_scatter_records(self, df, x_field, y_field, x_label, y_label):
        records = df[[x_field, y_field]].to_dict(orient='records')
        for rec in records:
            rec[x_label] = rec.pop(x_field)
            rec[y_label] = rec.pop(y_field)
        return records
