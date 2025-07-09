import math
from pyexpat.errors import messages
from applications.getdata.models import SensorsData
from django.db.models import Max
from math import atan, sqrt
from core.logger_config import logger_AFD



class FanAdministrator:
    def __init__(self, project, request=None) -> None:
        self.configuracion = project
        self.item_sensors = None
        self.pbs1 = None
        self.request = request
        self.temperatura_bh_s1 = None
        
        self.velocidad_aire_sensores = {
            'sensor1': 0,
            'sensor2': 0
        }
        self.presion_dinamica = {
            'sensor1': 0,
            'sensor2': 0
        }
        self.caudal_aire_sensores = {
            'sensor1': 0,
            'sensor2': 0
        }
        self.densidad_aire_sensores = {
            'sensor1': 0,
            'sensor2': 0
        }
        self.start()


    def start(self) -> None:
        """
        areas_ducto: dict, ejemplo: {'sensor1': ..., 'sensor2': ...}
        densidades_aire: dict, ejemplo: {'sensor1': ..., 'sensor2': ...}
        """
        
        # Obtiene el registro más reciente de SensorsData
        latest_record_sensors = SensorsData.objects.using('sensorDB').aggregate(Max('id'))
        max_id_sensors = latest_record_sensors['id__max']
        self.item_sensors = SensorsData.objects.using('sensorDB').get(id=max_id_sensors)

        # SENSOR 1
        pt1 = self.item_sensors.pt1
        ps1 = self.item_sensors.ps1
        self.presion_dinamica['sensor1'] = pt1 - ps1
        
        area_ducto = self.configuracion.ducto.area
        
        self.tbs2 = self.item_sensors.Tbs2 # Tbs2
        Tbs1 = self.item_sensors.Tbs1 # Tbs1
        HRs1 =  self.item_sensors.HRs1 # HRs1
        Tbs2 = self.item_sensors.Tbs2 # Tbs2
        HRs2 = self.item_sensors.HRs2 # HRs2
        self.pbs1 = self.item_sensors.Pbs1  # Pbs1
        self.pbs2 = self.item_sensors.Pbs2  # Pbs2
        
        self.tbs1 = round(self.calculate_tbh(Tbs1, HRs1),1)
        self.temperatura_bh_s1 = round(self.calculate_tbh(Tbs2, HRs2),1)

        

        self.caudal_aire_sensores['sensor1'] = self.caudal_aire_sensor(
            velocidad_aire_sensor=self.velocidad_aire_sensores['sensor1'],
            area_ducto=area_ducto
        )
        self.densidad_aire_sensores['sensor1'] = self.densidad_del_aire_s1()

        try:
            self.velocidad_aire_sensores['sensor1'] = self.velocidad_aire_sensor(
                presion_dinamica_sensor=self.presion_dinamica['sensor1'],
                densidad_aire_sensor=self.densidad_aire_sensores['sensor1']
            )
        except Exception as e:
            raise Exception(f"No se pudo calcular la velocidad del aire, presión dinámica: {self.presion_dinamica['sensor1']} densidad del aire s1: {self.densidad_aire_sensores['sensor1']}")

        # SENSOR 2
        pt2 = self.item_sensors.pt2
        ps2 = self.item_sensors.ps2
        self.presion_dinamica['sensor2'] = pt2 - ps2
        self.densidad_aire_sensores['sensor2'] = self.densidad_del_aire_s2()
        
        try:

            self.velocidad_aire_sensores['sensor2'] = self.velocidad_aire_sensor(
                presion_dinamica_sensor=self.presion_dinamica['sensor2'],
                densidad_aire_sensor=self.densidad_aire_sensores['sensor2']
            )
        except Exception as e:
            if not self.request is None:
                messages.warning(self.request, e)
        self.caudal_aire_sensores['sensor2'] = self.caudal_aire_sensor(
            velocidad_aire_sensor=self.velocidad_aire_sensores['sensor2'],
            area_ducto=area_ducto
        )
        
        

    # @staticmethod
    def velocidad_aire_sensor(self, presion_dinamica_sensor, densidad_aire_sensor):
        primera_ = 2 * presion_dinamica_sensor
        try:
            return math.sqrt(primera_/densidad_aire_sensor)
        except (ValueError, ZeroDivisionError):
            raise Exception(f"No se pudo calcular la velocidad del aire, presión dinámica: {presion_dinamica_sensor} densidad aire: {densidad_aire_sensor}")
            

    # @staticmethod
    def caudal_aire_sensor(self, velocidad_aire_sensor, area_ducto):
        """
        Q = velocidad * área
        """
        try:
            return velocidad_aire_sensor * area_ducto
        except (ValueError, ZeroDivisionError):
            raise Exception(f"No se pudo calcular el caudal del aire; valores actuales:  velocidad aire: {velocidad_aire_sensor} area ducto: {area_ducto}")


        
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

    def densidad_del_aire_s1(self):
        return round((self.pbs1 - self.e()) / (287.04 * (self.tbs1 + 273.15)), 3)
    
    def densidad_del_aire_s2(self):
        return round((self.pbs2 - self.e()) / (287.04 * (self.tbs2 + 273.15)), 3)
    
    def calculate_tbh(self, tbs, hr):
        return tbs * atan(0.151977 * sqrt(hr + 8.313659)) + atan(tbs + hr) - atan(hr - 1.6763) + 0.00391838 * pow(hr, 1.5) * atan(0.023101 * hr) - 4.686035


