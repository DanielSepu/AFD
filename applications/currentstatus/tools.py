

from math import sqrt


def calculate_perdida_choque_codos(total_codos, mid_densidad, Q1, project, Qf):
    """
    Calcula la perdida por choque de los codos a partir de la cantidad de codos.

    Args:
        total_codos (int): la cantidad de codos asignada al proyecto
        mid_densidad (int): la mita de la densidad del aire, este es un valor obtenido desde los sensores
        Q1 (int): el caudal del ventilador, este valor corresponde al q1 del modelo SensorsData
        project (object): objeto del proyecto actual ,
        Qf (int): corresponde al resultado obtenido de modelo sensorDB, el ultimo registro
    Returns:
        float: la perdida por choque de los codos
    """
    
    first_section = 0.5 * mid_densidad
    sumatoria_Sl = 0
    for num in range(total_codos):
        second_section = 0
        if num == 1:

            second_section = aply_first_codo(project, Q1, project.ducto.t_ducto)

        if num == 2:
            second_section = aply_second_codo(project, Q1, project.ducto.t_ducto, Qf)
        
        if num >= 3:
            second_section = aply_third_codo(project, Q1, project.ducto.t_ducto, Qf)
        
        SLcodo = first_section * second_section
        sumatoria_Sl += SLcodo
    
    return sumatoria_Sl


def aply_first_codo(project, Q1,type):
    if type == "ovalado":
        area = project.ducto.area 

        return pow((Q1/area),2)
        
    if type == "circular":
        mid_diametro = project.ducto.diametro/2
        cuadrado_mid_diametro = pow(mid_diametro,2)
        down_section = 3.14159 * cuadrado_mid_diametro
        return pow((Q1/down_section),2)


def aply_second_codo(project, Q1,type, Qf):
    up_section = Q1 - (0.25 * (Q1 -Qf ))
    if type == "ovalado":

        return pow((up_section/project.ducto.area),2)
        
    if type == "circular":
        mid_diametro = project.ducto.diametro/2

        down_section = 3.14159 * pow(mid_diametro,2)

        return  pow((up_section/down_section), 2)
    
def aply_third_codo(project, Q1,type, Qf):
    up_section = sqrt(Q1 * Qf)
    if type == "ovalado":

        return pow((up_section/project.ducto.area),2)
        
    if type == "circular":
        mid_diametro = project.ducto.diametro/2

        down_section = 3.14159 * pow(mid_diametro,2)

        return  pow((up_section/down_section), 2)
    