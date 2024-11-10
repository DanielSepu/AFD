

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
    dict_resultado_operacion = {

    }
    first_section = 0.5 * mid_densidad
    print(f"primera parte: {first_section}")
    sumatoria_Sl = 0
    print(f"Tipo de ducto: {project.ducto.t_ducto}")
    print(f"total codos: {total_codos}")
    second_section = 0

    first_codo = 0
    second_codo = 0
    third_codo = 0
    for num in range(total_codos):
        num = num + 1
        
        if num == 1:

            first_codo = aply_first_codo(first_section, project, Q1, project.ducto.t_ducto)
            print(f"perdida {num} codo: {first_codo} Q1: {Q1}")
        if num == 2:
            second_codo = aply_second_codo(first_section, project, Q1, project.ducto.t_ducto, Qf)
            print(f"perdida {num} codo: {second_codo}")
            sumatoria_Sl = first_codo+second_codo
        if num >= 3:
            third_codo = aply_third_codo(first_section, project, Q1, project.ducto.t_ducto, Qf)
            print(f"perdida {num} codo: {third_codo}")
            
            
            sumatoria_Sl = first_codo+second_codo+ (total_codos-2)*third_codo
    print(f"calcular perdida de choque de codos: {sumatoria_Sl}")
    return sumatoria_Sl


def aply_first_codo(first_section, project, Q1,type):
    Q_codo_1 = Q1**2
    if type == "ovalado":
        area = project.ducto.area 
        form_part_2 =  1/(area*area)
        
        print(f"codo 1: Q_codo_1: {Q_codo_1} first_section: {first_section} form_part_2: {form_part_2}")
        return first_section*form_part_2*Q_codo_1
        
    if type == "circular":
        area_ducto_circular_ = area_ducto_circular(project)
        formula_parte_2_ducto_circular = 1/(area_ducto_circular_*area_ducto_circular_)
        
        return first_section*formula_parte_2_ducto_circular*Q_codo_1


def aply_second_codo(first_section, project, Q1,type, Qf):
    up_section =  (Q1-0.25 * (Q1 -Qf ))**2
    if type == "ovalado":
        area = project.ducto.area
        area_ducto_ovalado = 1/(area*area)
        return first_section*up_section*area_ducto_ovalado
        
    if type == "circular":
        area_ducto_circular_ = area_ducto_circular(project)
        formula_parte_2_ducto_circular = 1/(area_ducto_circular_*area_ducto_circular_)
        
        return  first_section*formula_parte_2_ducto_circular*up_section
    
def aply_third_codo(first_section, project, Q1,type, Qf):
    
    up_section = sqrt(Q1 * Qf)
    if type == "ovalado":
        area_ducto_ovalada = project.ducto.area
        formula_parte_2_ducto_ovalado = 1/(area_ducto_ovalada*area_ducto_ovalada)
        Q_codos345 = up_section**2
        
        return first_section*formula_parte_2_ducto_ovalado*Q_codos345
        
    if type == "circular":
        area_ducto_circular_ = area_ducto_circular(project)
        formula_parte_2_ducto_circular =  1/(area_ducto_circular_*area_ducto_circular_)
        Q_codos_3 = up_section**2
        
        return  first_section*formula_parte_2_ducto_circular*Q_codos_3
    
def area_ducto_circular(project):
    return 3.14159 * pow(project.ducto.diametro/2000,2)

def area_inlet_bell(project):
    return 3.14159 *(project.ventilador.vmm/2000)**2

def area_ducto_ovalado(project):
    return 3.14159*(project.ducto.area*project.ducto.area)