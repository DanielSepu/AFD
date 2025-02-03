

from math import sqrt
#from scipy.optimize import curve_fit
import numpy as np



def calculate_perdida_choque_codos(total_codos, mid_densidad, Q1, project, Qf):
    """
            Calcula la perdida por choque de los codos a partir de la cantidad de codos.
            Args:
                total_codos (int): la cantidad de codos asignada al proyecto
                mid_densidad (int): la mitad de la densidad del aire, este es un valor obtenido desde los sensores
                Q1 (int): el caudal del ventilador, este valor corresponde al q1 del modelo SensorsData
                project (object): objeto del proyecto actual
                Qf (int): corresponde al resultado obtenido de modelo sensorDB, el último registro
            Returns:
                dict: diccionario con todas las variables calculadas
                float: la pérdida total por choque de los codos
        """
    # Inicializar el diccionario para almacenar todas las variables calculadas
    
    variables = {}
    # Cálculo de la primera sección
    first_section = 0.5 * mid_densidad
    variables['mid_densidad'] = mid_densidad
    variables['first_section'] = first_section
    
    variables['total_codos'] = total_codos
    variables['Q1'] = Q1
    variables['Qf'] = Qf
    variables['factor_choque_codo_X'] = 0.5
    sumatoria_Sl = 0
    first_codo = 0
    second_codo = 0
    third_codo = 0
    
    for num in range(total_codos):
        num += 1
        if num == 1:
            first_codo = aply_first_codo(first_section, project, Q1, project.ducto.t_ducto)
            print(f"first_codo: {first_codo}")
            variables['first_codo'] = first_codo
            variables['q_codo_1'] = q_codo_1(Q1)
        if num == 2:
            second_codo = aply_second_codo(first_section, project, Q1, project.ducto.t_ducto, Qf)
            print(f"second_codo: {second_codo}")
            sumatoria_Sl = first_codo + second_codo
            variables['second_codo'] = second_codo
            variables['q_codo_2'] = q_codo_2(Q1, Qf)
            variables['sumatoria_Sl'] = sumatoria_Sl
        if num >= 3:
            third_codo = aply_third_codo(first_section, project, Q1, project.ducto.t_ducto, Qf)
            print(f"third_codo: {third_codo}")
            sumatoria_Sl = first_codo + second_codo + (total_codos - 2) * third_codo
            variables['third_codo'] = third_codo
            variables['sumatoria_Sl'] = sumatoria_Sl
            variables['q_codo_3'] = q_codo_3(Q1, Qf)
    variables["area_ducto_circular"] = area_ducto_circular(project)
    variables["area_ducto_ovalado"] = project.ducto.area
    variables['final_sumatoria_Sl'] = sumatoria_Sl
    variables['formula_parte_2_ovalado'] = formula_parte_2_ovalado(project)
    variables['formula_parte_2_'] = formula_parte_2_circular(project)
    # Retornar el diccionario de variables y el resultado final
    return variables, sumatoria_Sl

def q_codo_1(Q1):
    return Q1**2

def aply_first_codo(first_section, project, Q1,type):
    Q_codo_1 = q_codo_1(Q1)
    if type == "ovalado":
        area = project.ducto.area 
        form_part_2 =  1/(area*area)
        return first_section*form_part_2*Q_codo_1
        
    if type == "circular":
        area_ducto_circular_ = area_ducto_circular(project)
        print(f"area_ducto_circular calculada: {area_ducto_circular_}")
        formula_parte_2_ducto_circular = 1/(area_ducto_circular_*area_ducto_circular_)
        
        return first_section*formula_parte_2_ducto_circular*Q_codo_1

def formula_parte_2_circular(project):
    area_ducto_circular_ = area_ducto_circular(project)
    return 1/(area_ducto_circular_*area_ducto_circular_)


def q_codo_2(Q1, Qf):
    return (Q1-0.25 * (Q1 -Qf ))**2

def aply_second_codo(first_section, project, Q1,type, Qf):
    up_section =  q_codo_2(Q1, Qf)
    if type == "ovalado":
        area = project.ducto.area
        area_ducto_ovalado = 1/(area*area)
        return first_section*up_section*area_ducto_ovalado
        
    if type == "circular":
        #area_ducto_circular_ = area_ducto_circular(project)
        formula_parte_2_ducto_circular = formula_parte_2_circular(project)
        print(f"formula_parte_2_ducto_circular: {formula_parte_2_ducto_circular} ")
        print(f"first_section: {first_section} up_section: {up_section}")
        return  first_section*formula_parte_2_ducto_circular*up_section

def formula_parte_2_ovalado(project):
    area_ducto_ovalada = project.ducto.area
    formula_parte_2_ducto_ovalado = 1/(area_ducto_ovalada*area_ducto_ovalada)
    return formula_parte_2_ducto_ovalado

def q_codo_3(Q1, Qf):
    return sqrt(Q1 * Qf)**2

def aply_third_codo(first_section, project, Q1,type, Qf):
    
    up_section = q_codo_3(Q1, Qf)
    if type == "ovalado":
        formula_parte_2_ducto_ovalado = formula_parte_2_ovalado(project)
        Q_codos345 = q_codo_3(Q1, Qf)
        
        return first_section*formula_parte_2_ducto_ovalado*Q_codos345
        
    if type == "circular":
        area_ducto_circular_ = area_ducto_circular(project)
        formula_parte_2_ducto_circular =  1/(area_ducto_circular_*area_ducto_circular_)
        Q_codos_3 = q_codo_3(Q1, Qf)
        
        return  first_section*formula_parte_2_ducto_circular*Q_codos_3
    
def area_ducto_circular(project):
    return 3.14159 * pow(project.ducto.diametro/2000,2)

def area_inlet_bell(project):
    return 3.14159 *(project.ventilador.vmm/2000)**2

def area_ducto_ovalado(project):
    return 3.14159*(project.ducto.area*project.ducto.area)



def goal_seek_custom(ajuste_cubico, r_actual, initial_guess=0.5, tolerance=1e-6, max_iterations=100):
    """
    Realiza el Goal Seek para encontrar el valor de X que satisface la ecuación goal_seek = 0.

    Parámetros:
    - ajuste_cubico: Coeficientes [a3, a2, a1, a0] del polinomio cúbico.
    - r_actual: Valor de la resistencia actual.
    - initial_guess: Valor inicial para X.
    - tolerance: Precisión deseada (valor cercano a 0 para goal_seek).
    - max_iterations: Número máximo de iteraciones permitidas.

    Retorna:
    - El valor de X que satisface la ecuación.
    """
    X = initial_guess  # Iniciar con un valor inicial

    for i in range(max_iterations):
        # Calcular ecuaciones
        ecuacion1 = (
            ajuste_cubico[0] * X**3 +
            ajuste_cubico[1] * X**2 +
            ajuste_cubico[2] * X +
            ajuste_cubico[3]
        )
        ecuacion2 = r_actual * X**2
        
        # Evaluar la función goal_seek
        goal_seek = ecuacion1 - ecuacion2
        
        # Verificar si estamos dentro de la tolerancia
        if abs(goal_seek) < tolerance:
            print(f"Goal Seek convergió después de {i+1} iteraciones.")
            return ecuacion1, ecuacion2, X
        
        # Calcular la derivada numérica de la ecuación goal_seek
        derivative = (
            3 * ajuste_cubico[0] * X**2 +
            2 * ajuste_cubico[1] * X +
            ajuste_cubico[2] -
            2 * r_actual * X
        )
        
        if derivative == 0:
            raise ValueError("La derivada es cero, no se puede continuar la búsqueda.")

        # Actualizar X usando el método de Newton-Raphson
        X -= goal_seek / derivative

    raise ValueError("Goal Seek no convergió en el número máximo de iteraciones.")


