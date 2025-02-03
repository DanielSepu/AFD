

from math import sqrt
import math

from modules.semaforo import Semaforo


def presion_dinamica_sensor_1(presion_t_s1, presion_estatica_s1):
    return presion_t_s1 - presion_estatica_s1
    
def velocidad_aire_sensor(presion_dinamica_sensor, densidad_aire_sensor1):
    primera_ = 2 * presion_dinamica_sensor
    return math.sqrt(primera_/densidad_aire_sensor1)

def caudal_aire_sensor1(velocidad_aire_sensor1, area_ducto):
    return round(velocidad_aire_sensor1*area_ducto,1)

def velocidad_aire_para_Q(presion_total, presion_dinamica_sensor1, densidad_aire_sensor1):
    primera_ = 2 * presion_dinamica_sensor1
    
    return math.sqrt(primera_/densidad_aire_sensor1)

def calcular_Q(velocidad_aire_sensor, area_ducto):
    return round(velocidad_aire_sensor1*area_ducto,1)

def densidad_aire_sensor1(diccionario):
    pass

def caudal_de_la_frente(Q2, Lc, pt2, Lf):
    return Q2 - Lc*0.5*pt2*Lf /100000
    
def ajuste_rpm():
    pass


class calculo_densidad_aire_sensor:
    def __init__(self, tbs1, temperatura_bh_s1, pbs1):
        self.tbs1 = tbs1
        self.temperatura_bh_s1 = temperatura_bh_s1
        self.pbs1 = pbs1

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
    tbs1 = 30.7
    temperatura_bh_s1 = 20.5
    pbs1 = 95362

    calculo = calculo_densidad_aire_sensor(tbs1, temperatura_bh_s1, pbs1)
    print(f"esd: {calculo.esd()}")
    print(f"esw: {calculo.esw()}")
    print(f"xs: {calculo.xs()}")
    print(f"lw: {calculo.lw()}")
    print(f"s: {calculo.s()}")
    print(f"x: {calculo.x()}")
    print(f"e: {calculo.e()}")
    print(f"densidad del aire: {calculo.densidad_del_aire()}")
    
    
    presion_dinamica = presion_dinamica_sensor_1(709, 490 )
    print(f"presion dinamica: {presion_dinamica}")
    print(f"densidad_del_aire: {calculo.densidad_del_aire()}")
    velocidad_aire_sensor1 = velocidad_aire_sensor(presion_dinamica, calculo.densidad_del_aire())
    print(f"velocidad_aire: {velocidad_aire_sensor1}")
    area_ducto = 0.28
    caudal_del_aire = caudal_aire_sensor1(velocidad_aire_sensor1, area_ducto)
    
    print(f"caudal_del_aire: {caudal_del_aire}")
    
    
