from django import forms
from applications.getdata.models import Ventilador, CurvaDiseno, Ducto, EquipamientoDiesel, Tipo_Equipamiento_Diesel, Caracteristicas_Ventilador, Proyecto, Sistema_Partida
from django.core.validators import MaxValueValidator
from django.utils.safestring import mark_safe

##################### Extractores de nombres para los select, de otro modo se ven: "table object (1)"
class CustomMMCF(forms.ModelMultipleChoiceField):
   def label_from_instance(self, member):
      return "%s" % member.nombre

class CustomMCF(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.modelo +' | '+ obj.idu

#####################
    
class VentiladorForm(forms.ModelForm):
    def clean_polos(self):
        polos = self.cleaned_data['polos']
        if polos % 2 != 0 or polos < 2:
            raise forms.ValidationError("Polos inválidos")
        return polos
    
    modelo = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el modelo'})
    )
    
    polos = forms.IntegerField(
        widget=forms.Select(
            choices=[(2, '2'), (4, '4'), (6, '6'), (8, '8'), (10, '10'), (12, '12')],
            attrs={'class': 'form-select'}
        ),
        label="Polos"
    )

    img_ventilador = forms.ImageField(
        label='Imagen del ventilador',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    vmm = forms.FloatField(
        label='V (mm)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese V'})
    )
    
    amm = forms.FloatField(
        label='A (mm)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese A'})
    )
    
    nmm = forms.FloatField(
        label='N (mm)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese N'})
    )
    
    hp = forms.FloatField(
        label='Potencia motor (kW)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Potencia'})
    )
    
    accesorios = CustomMMCF(
        queryset=Caracteristicas_Ventilador.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
        label="Accesorios"
    )
    
    class Meta:
        model = Ventilador
        fields = ['modelo', 'vmm', 'amm', 'nmm', 'hp', 'polos', 'img_ventilador', 'accesorios']
        labels = {
            'modelo': 'Modelo',
            'vmm': 'V',
            'amm': 'A',
            'rmm': 'R',
            'hp': 'Potencia (HP)'
        }
        field_order = ['modelo', 'vmm', 'amm', 'nmm', 'hp', 'img_ventilador', 'accesorios']
    
    class Meta:
        model = Ventilador
        fields = ['modelo', 'vmm', 'amm', 'nmm', 'hp', 'polos',  'img_ventilador','accesorios']
        labels = {
            'modelo': 'Modelo',
            'vmm': 'V',
            'amm': 'A',
            'rmm': 'R',
            'hp': 'Potencia (HP)'
        }
        field_order = ['modelo', 'vmm', 'amm', 'nmm', 'hp',  'img_ventilador','accesorios']

    
      
class CurvaDisenoForm(forms.ModelForm):
    idu = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID'}),
        label='ID/Nombre'
    )
    ventilador = CustomMCF(
        queryset=Ventilador.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})  # Clase Bootstrap para select
    )

    angulo = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el ángulo (°)'}),
        label='θ °'
    )
    
    rpm = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese RPM'}),
        label='RPM'
    )
    
    densidad = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese densidad (kg/m³)'}),
        label='ρ (kg/m³)'
    )

    datos_curva = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = CurvaDiseno
        fields = ['idu', 'ventilador', 'angulo', 'rpm', 'densidad', 'datos_curva']
        labels = {
            'idu': '/Nombre',
            'angulo': 'θ °',
            'rpm': 'RPM',
            'densidad': 'ρ (kg/m³)',
        }
    def clean(self):
        cleaned_data = super().clean()
        post = self.data  # Contiene todos los campos POST
        print(post)
        # Manejo de caudal_0 y presion_0
        caudal_0 = post.get('caudal_0')
        presion_0 = post.get('presion_0')
        potencia_0 = post.get('potencia_0')

        # Si el valor es una lista, toma el primer elemento
        if isinstance(caudal_0, list):
            caudal_0 = caudal_0[0] if caudal_0 else 0.0
        if isinstance(presion_0, list):
            presion_0 = presion_0[0] if presion_0 else 0.0
        if isinstance(presion_0, list):
            potencia_0 = potencia_0[0] if potencia_0 else 0.0

        # Convierte a float (maneja errores)
        try:
            caudal_0 = float(caudal_0)
        except (TypeError, ValueError):
            print(f"Error en el campo caudal_0: {caudal_0}")
            caudal_0 = 0.0

        try:
            presion_0 = float(presion_0)
        except (TypeError, ValueError):
            print(f"Error en el campo presion_0: {presion_0}")
            presion_0 = 0.0

        # Inicializa las listas
        caudal_list = [caudal_0]
        presion_list = [presion_0]
        potencia_list = [potencia_0]

        # Manejo de los demás campos (caudal_1, presion_1, etc.)
        i = 1
        while True:
            c = post.get(f'caudal_{i}')
            p = post.get(f'presion_{i}')
            pt = post.get(f'potencia_{i}')

            # Si no hay más campos, sal del bucle
            if c is None and p is None and pt is None:
                break

            # Convierte a float (maneja errores)
            try:
                c = float(c)
            except (TypeError, ValueError):
                print(f"Error en el campo caudal_{i}: {c}")
                c = 0.0

            try:
                p = float(p)
            except (TypeError, ValueError):
                print(f"Error en el campo presion_{i}: {p}")
                p = 0.0

            try:
                pt = float(pt)
            except (TypeError, ValueError):
                print(f"Error en el campo potencia_{i}: {pt}")
                pt = 0.0

            caudal_list.append(c)
            presion_list.append(p)
            potencia_list.append(pt)
            i += 1

        # Reconstruye el diccionario final
        cleaned_data['datos_curva'] = {
            "caudal": caudal_list,
            "presion": presion_list,
            "potencia": potencia_list,
        }

        return cleaned_data

class DuctoForm(forms.ModelForm):
    DUCTO_CHOICES = [
        ('circular', 'Circular'),
        ('ovalado', 'Ovalado'),
    ]
    
    idu = forms.CharField(
        label='ID/Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el ID'})
    )
    
    t_ducto = forms.ChoiceField(
        label='Tipo de ducto',
        choices=DUCTO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Ingrese el tipo de ducto'})
    )
    
    f_friccion = forms.FloatField(
        label='Factor de fricción (kg/m³) (opcional)',
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el factor de fricción'})
    )
    
    f_fuga = forms.FloatField(
        label='Factor de fuga (mm²/m²) (opcional)',
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el factor de fuga'})
    )
    
    diametro = forms.FloatField(
        label='Diámetro (cm)',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el diámetro'}),
    )
    
    area = forms.FloatField(
        label='Área (m²)',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Área calculada', 'readonly': 'true'}),
    )

    t_acople = forms.CharField(
        label='Tipo de acople',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el tipo de acople'})
    )
    
    largo = forms.FloatField(
        label='Largo (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el largo'})
    )
    Ldsf = forms.FloatField(
        label='longitud de ducto desde el sensor 2 hasta la frente (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'longitud de ducto desde el sensor 2 hasta la frente (m)'})
    )
    class Meta:
        model = Ducto
        fields = ['idu', 't_ducto','diametro','area', 'f_friccion', 'f_fuga', 't_acople', 'largo', 'Ldsf']
        
        labels = {
            'idu': 'ID/Nombre',
            't_ducto': 'Tipo de ducto',
            'f_friccion': 'Factor de fricción(K) (opcional)',
            'f_fuga': 'Factor de fuga(L) (opcional)',
            't_acople': 'Tipo de acople',
            'largo': 'Largo (m)',
            'Ldsf': 'longitud de ducto desde el sensor 2 hasta la frente (m)'
        }
    


class EquipDieselForm(forms.ModelForm):

    class CustomEDN(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.nombre

    potencia = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'onchange': 'Funcion()',
            'value': '0',
            'class': 'form-control',  # Clase Bootstrap para estilo
            'placeholder': 'Ingrese potencia (HP)'
        }),
        label='Potencia (HP)'
    )
    
    qr_fabricante = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'onchange': 'Funcion2()',
            'class': 'form-control',  # Clase Bootstrap para estilo
            'placeholder': 'Ingrese requerimiento de caudal m³/s (opcional)'
        }),
        label='Requerimiento de caudal informado por el fabricante m³/s (opcional)',
        required=False
    )
    
    qr_calculado = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Clase Bootstrap para estilo
            'placeholder': 'Requerimiento de caudal (m³/s)'  # Placeholder informativo
        }),
        label='Requerimiento de caudal (m³/s)',
    )
    
    tipo = CustomEDN(
        queryset=Tipo_Equipamiento_Diesel.objects.all(),
        label='Tipo de equipamiento',
        widget=forms.Select(attrs={'class': 'form-select'})  # Clase Bootstrap para select
    )

    class Meta:
         model = EquipamientoDiesel
         fields = ['idu','tipo','modelo_diesel','potencia','qr_fabricante','qr_calculado']
         labels = {
            'idu': 'ID/Nombre',
            'modelo_diesel':  'Modelo',
            #'tipo': 'Tipo Equio'
         }

class ProyectoForm(forms.ModelForm):
    n_carga_choices = (
      ('liviana','Liviana'),
      ('moderada','Moderada'),
      ('pesada','Pesada')
   )
    t_trabajo_choices = (
      ('trabajo continuo','Trabajo continuo'),
      ('75-25','75% trabajo - 25%'),
      ('50-50','50% trabajo - 50%'),
      ('25-75','25% trabajo - 75%'),
   )
    class CustomPFV(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.modelo + ' | ' + obj.idu

    class CustomPFI(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.idu

    class CustomPMMCF(forms.ModelMultipleChoiceField):
        def label_from_instance(self, obj):
            return obj.modelo_diesel + ' | ' + obj.idu

    class CustomPSP(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.nombre

    ventilador = CustomPFV(
        queryset=Ventilador.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Ventilador'
    )
    
    curva_diseno = CustomPFI(
        queryset=CurvaDiseno.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Curva Diseño'
    )
    
    ducto = CustomPFI(
        queryset=Ducto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Ducto'
    )
    
    s_partida = CustomPSP(
        queryset=Sistema_Partida.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sistema de partida'
    )
    
    codos = forms.IntegerField(
        label='Codos',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número de codos'})
    )

    caudal_requerido = forms.FloatField(
        label='Caudal requerido (m³/s)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control ', 
            'placeholder': 'Ingrese el caudal requerido',
            'readonly': 'readonly',
            'value': 0
            })
    )
    
    ancho_galeria = forms.FloatField(
        label='Ancho galería (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el ancho de la galería'})
    )
    
    alto_galeria = forms.FloatField(
        label='Alto galería (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el alto de la galería'})
    )

    area_galeria = forms.FloatField(
        label='Área galería (m²)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el área de la galería'})
    )
    factor = forms.FloatField(
        validators=[MaxValueValidator(100)],  # Limita el valor máximo a 100
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese un valor (máximo 100)',
        }),
        label="Factor (%)"
    )

    potencia = forms.FloatField(
        label='Potencia (kw)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la potencia'})
    )

    dis_e_sens = forms.FloatField(
        label='Distancia entre sensores (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la distancia entre sensores'})
    )
    lf = forms.FloatField(
        label='Longitud de ducto desde el sensor 2 hasta la frente (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'longitud de ducto desde el sensor 2 hasta la frente (m)'})
    )
    nivel_carga = forms.ChoiceField(
        label='Nivel de carga',
        choices=n_carga_choices,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nivel de carga'})
    )
    tipo_trabajo = forms.ChoiceField(
        label='Tipo de trabajo',
        choices=t_trabajo_choices,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Ingrese el tipo de trabajo'})
    )


    class Meta:
        model = Proyecto
        fields = ['id', 'ventilador', 's_partida', 'potencia','curva_diseno','nivel_carga', 'tipo_trabajo', 'ducto', 'lf','caudal_requerido', 'codos', 'ancho_galeria', 'alto_galeria', 'area_galeria', 'factor', 'dis_e_sens']
        labels = {
            'ancho_galeria': 'Ancho galería',
            'alto_galeria': 'Alto galería',
            'potencia': 'Potencia (kw)',
            'dis_e_sens': 'Distancia entre sensores (m)',
            'lf': 'longitud de ducto desde el sensor 2 hasta la frente (m)'
        }

    field_order = ['id', 'ventilador', 'potencia', 's_partida', 'curva_diseno', 'ducto', 'caudal_requerido', 'codos', 'ancho_galeria', 'alto_galeria', 'factor', 'area_galeria', 'dis_e_sens', 's_partida']

class SistemaPartidaForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del sistema de partida'})
    )
    class Meta:
        model = Sistema_Partida
        fields = ['nombre']

class TipoEquipamientodieselForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del equipo disel'})
    )

    class Meta:
        model = Tipo_Equipamiento_Diesel
        fields = ['nombre']

class Caracteristicas_VentiladorForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del accesorio'})
    )
    factor_choque = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Factor de choque'}),
        label='Factor de choque'
    )
    class Meta:
        model = Caracteristicas_Ventilador
        verbose_name = 'Caracteristicas_ventilador'
        verbose_name_plural = 'Caracteristicas_ventiladors'
        fields = ['nombre', 'factor_choque']