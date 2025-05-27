import math
from django.db.models import Max
from applications.getdata.models import SensorsData



def presion_dinamica_sensor_1(presion_t_s1, presion_estatica_s1):
    return presion_t_s1 - presion_estatica_s1
    
def velocidad_aire_sensor(presion_dinamica_sensor, densidad_aire_sensor1):
    primera_ = 2 * presion_dinamica_sensor
    return math.sqrt(primera_/densidad_aire_sensor1)

def caudal_aire_sensor1(velocidad_aire_sensor1, area_ducto):
    return round(velocidad_aire_sensor1*area_ducto,1)


def caudal_de_la_frente(Q2, Lc, pt2, Lf):
    return Q2 - Lc*0.5*pt2*Lf /100000



    
    
