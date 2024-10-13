from django import forms
from applications.getdata.models import Ventilador, CurvaDiseno, Ducto, EquipamientoDiesel, Tipo_Equipamiento_Diesel, Caracteristicas_Ventilador, Proyecto, Sistema_Partida

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
        )
    )

    img_ventilador = forms.ImageField(
        label='Imagen del ventilador',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    vmm = forms.FloatField(
        label='V',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese V'})
    )
    
    amm = forms.FloatField(
        label='A',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese A'})
    )
    
    rmm = forms.FloatField(
        label='R',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese R'})
    )
    
    hp = forms.FloatField(
        label='Potencia (HP)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Potencia'})
    )
    accesorios = CustomMMCF(
        queryset=Caracteristicas_Ventilador.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
        label='Accesorios'
    )
    class Meta:
        model = Ventilador
        fields = ['idu', 'modelo', 'vmm', 'amm', 'rmm', 'hp', 'polos', 'img_ventilador', 'accesorios']
        labels = {
            'idu': 'ID',
            'modelo': 'Modelo',
            'vmm': 'V',
            'amm': 'A',
            'rmm': 'R',
            'hp': 'Potencia (HP)'
        }
        field_order = ['idu', 'modelo', 'vmm', 'amm', 'rmm','hp','img_ventilador', 'accesorios']

      
class CurvaDisenoForm(forms.ModelForm):
    idu = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID'}),
        label='ID'
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
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese densidad (kg/m3)'}),
        label='ρ (kg/m3)'
    )

    class Meta:
        model = CurvaDiseno
        fields = ['idu', 'ventilador', 'angulo', 'rpm', 'densidad']
        labels = {
            'idu': 'ID',
            'angulo': 'θ °',
            'rpm': 'RPM',
            'densidad': 'ρ (kg/m3)',
        }


class DuctoForm(forms.ModelForm):
    idu = forms.CharField(
        label='ID',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el ID'})
    )
    
    t_ducto = forms.CharField(
        label='Tipo de ducto',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el tipo de ducto'})
    )
    
    f_friccion = forms.FloatField(
        label='Factor de fricción(K) (opcional)',
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el factor de fricción'})
    )
    
    f_fuga = forms.FloatField(
        label='Factor de fuga(L) (opcional)',
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el factor de fuga'})
    )
    
    t_acople = forms.CharField(
        label='Tipo de acople',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el tipo de acople'})
    )
    
    largo = forms.FloatField(
        label='Largo (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el largo'})
    )

    class Meta:
        model = Ducto
        fields = ['idu', 't_ducto', 'f_friccion', 'f_fuga', 't_acople', 'largo']
        labels = {
            'idu': 'ID',
            't_ducto': 'Tipo de ducto',
            'f_friccion': 'Factor de fricción(K) (opcional)',
            'f_fuga': 'Factor de fuga(L) (opcional)',
            't_acople': 'Tipo de acople',
            'largo': 'Largo (m)'
        }

    class Meta:
         model = Ducto
         fields = ['idu', 't_ducto','f_friccion', 'f_fuga', 't_acople', 'largo']
         labels = {
            'idu': 'ID',
            't_ducto':   'Tipo de ducto',
            't_acople':  'Tipo de acople',
            'largo':     'Largo ducto(m)',
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
            'placeholder': 'Ingrese requerimiento de caudal (opcional)'
        }),
        label='Requerimiento de caudal informado por el fabricante (opcional)',
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
            'idu': 'ID',
            'modelo_diesel':  'Modelo',
            #'tipo': 'Tipo Equio'
         }

class ProyectoForm(forms.ModelForm):

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
        label='Caudal requerido',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el caudal requerido'})
    )
    
    ancho_galeria = forms.FloatField(
        label='Ancho galería',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el ancho de la galería'})
    )
    
    alto_galeria = forms.FloatField(
        label='Alto galería',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el alto de la galería'})
    )

    area_galeria = forms.FloatField(
        label='Área galería',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el área de la galería'})
    )
    factor = forms.FloatField(
        label='Factor corrección (%)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '1', 'placeholder': 'Ingrese el factor de corrección'})
    )

    potencia = forms.FloatField(
        label='Potencia (W)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la potencia'})
    )

    dis_e_sens = forms.FloatField(
        label='Distancia entre sensores (m)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la distancia entre sensores'})
    )

    class Meta:
        model = Proyecto
        fields = ['id', 'ventilador', 'curva_diseno', 'ducto', 'caudal_requerido', 'codos', 'ancho_galeria', 'alto_galeria', 'area_galeria', 'factor', 's_partida', 'potencia', 'dis_e_sens']
        labels = {
            'ancho_galeria': 'Ancho galería',
            'alto_galeria': 'Alto galería',
            'potencia': 'Potencia (W)',
            'dis_e_sens': 'Distancia entre sensores (m)',
        }

    field_order = ['id', 'ventilador', 'curva_diseno', 'ducto', 'caudal_requerido', 'codos', 'ancho_galeria', 'alto_galeria', 'factor', 'area_galeria', 'potencia', 'dis_e_sens', 's_partida']
