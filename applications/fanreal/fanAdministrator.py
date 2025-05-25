import math
from applications.currentstatus.utils import calculo_densidad_aire_sensor
from applications.getdata.models import SensorsData
from django.db.models import Max

class FanAdministrator:
    def __init__(self, project) -> None:
        self.configuracion = project
        self.item_sensors = None
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
        
        calculador_densidad_aire = calculo_densidad_aire_sensor(self.configuracion)
        area_ducto = self.configuracion.ducto.area
        
        self.velocidad_aire_sensores['sensor1'] = self.velocidad_aire_sensor(
            presion_dinamica_sensor=self.presion_dinamica['sensor1'],
            densidad_aire_sensor=calculador_densidad_aire.densidad_del_aire_s1()
        )
        self.caudal_aire_sensores['sensor1'] = self.caudal_aire_sensor(
            velocidad_aire_sensor=self.velocidad_aire_sensores['sensor1'],
            area_ducto=area_ducto
        )
        self.densidad_aire_sensores['sensor1'] = calculador_densidad_aire.densidad_del_aire_s1()

        # SENSOR 2
        pt2 = self.item_sensors.pt2
        ps2 = self.item_sensors.ps2
        self.presion_dinamica['sensor2'] = pt2 - ps2
        self.densidad_aire_sensores['sensor2'] = calculador_densidad_aire.densidad_del_aire_s2()
        
        
        self.velocidad_aire_sensores['sensor2'] = self.velocidad_aire_sensor(
            presion_dinamica_sensor=self.presion_dinamica['sensor2'],
            densidad_aire_sensor=self.densidad_aire_sensores['sensor2']
        )
        self.caudal_aire_sensores['sensor2'] = self.caudal_aire_sensor(
            velocidad_aire_sensor=self.velocidad_aire_sensores['sensor2'],
            area_ducto=area_ducto
        )
        

    @staticmethod
    def velocidad_aire_sensor(presion_dinamica_sensor, densidad_aire_sensor):
        primera_ = 2 * presion_dinamica_sensor
        return math.sqrt(primera_/densidad_aire_sensor)

    @staticmethod
    def caudal_aire_sensor(velocidad_aire_sensor, area_ducto):
        """
        Q = velocidad * área
        """
        return velocidad_aire_sensor * area_ducto



