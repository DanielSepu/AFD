import math
from django.db.models import Max
from applications.getdata.models import SensorsData
from modules.utils import calculate_tbh


def presion_dinamica_sensor_1(presion_t_s1, presion_estatica_s1):
    return presion_t_s1 - presion_estatica_s1
    
def velocidad_aire_sensor(presion_dinamica_sensor, densidad_aire_sensor1):
    primera_ = 2 * presion_dinamica_sensor
    return math.sqrt(primera_/densidad_aire_sensor1)

def caudal_aire_sensor1(velocidad_aire_sensor1, area_ducto):
    return round(velocidad_aire_sensor1*area_ducto,1)


def caudal_de_la_frente(Q2, Lc, pt2, Lf):
    return Q2 - Lc*0.5*pt2*Lf /100000


class calculo_densidad_aire_sensor:
    def __init__(self, project):
        self.project = project
        self.item_sensors = None
        self.tbs1 = None
        self.temperatura_bh_s1 = None
        self.pbs1 = None
        
        latest_record_sensors = SensorsData.objects.using('sensorDB').aggregate(Max('id'))
        max_id_sensors = latest_record_sensors['id__max']
        self.item_sensors = SensorsData.objects.using('sensorDB').get(id=max_id_sensors)
        self.cargar_datos_iniciales()
        
        
    def cargar_datos_iniciales(self):
        Tbs1 = self.item_sensors.Tbs1 # Tbs1
        HRs1 =  self.item_sensors.HRs1 # HRs1
        
        Tbs2 = self.item_sensors.Tbs2 # Tbs2
        HRs2 = self.item_sensors.HRs2 # HRs2
        
        self.pbs1 = self.item_sensors.Pbs1  # Pbs1
        
        self.tbs1 = round(calculate_tbh(Tbs1, HRs1),1)
        self.temperatura_bh_s1 = round(calculate_tbh(Tbs2, HRs2),1)
        
    def esd(self):
        return round(610 * math.exp(17.27 * self.tbs1 / (237.3 + self.tbs1)), 3)

    def esw(self):
        return round(610 * math.exp(17.27 * self.temperatura_bh_s1 / (237.3 + self.temperatura_bh_s1)), 3)

    def xs(self):
        return round(0.622 * self.esw() / (self.pbs1 - self.esw()), 3)

    def lw(self):
        return round((2502.5 - 2.386 * self.temperatura_bh_s1) * 1000, 3)

    def s(self):
        return round(self.lw() * self.xs() + 1005 * self.temperatura_bh_s1, 3)

    def x(self):
        return round((self.s() - 1005 * self.tbs1) / (self.lw() + 1884 * (self.tbs1 - self.temperatura_bh_s1)), 3)

    def e(self):
        return round((self.pbs1 * self.x()) / (0.622 + self.x()), 3)

    def densidad_del_aire(self):
        return round((self.pbs1 - self.e()) / (287.04 * (self.tbs1 + 273.15)), 3)
    
if __name__ == "__main__":
    pass
    
    
