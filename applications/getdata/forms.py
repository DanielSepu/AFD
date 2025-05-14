from django import forms
from .models import IntervalosDeActualizacion, SensorsData, Simulador, Sistema_Partida, VdfData

class SistemaPartidaForm(forms.ModelForm):
    """
    Formulario para crear o editar elementos del modelo Sistema_Partida.
    """

    class Meta:
        model = Sistema_Partida
        fields = ['nombre']  # Campos que queremos incluir en el formulario
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
        }

        

class VdfDataForm(forms.ModelForm):
    class Meta:
        model = VdfData
        fields = ['fref', 'freal', 'vf', 'oc', 'power', 'powerc', 'rpm']
        widgets = {
            'fref': forms.NumberInput(attrs={'class': 'form-control'}),
            'freal': forms.NumberInput(attrs={'class': 'form-control'}),
            'vf': forms.NumberInput(attrs={'class': 'form-control'}),
            'oc': forms.NumberInput(attrs={'class': 'form-control'}),
            'power': forms.NumberInput(attrs={'class': 'form-control'}),
            'powerc': forms.NumberInput(attrs={'class': 'form-control'}),
            'rpm': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SensorsDataForm(forms.ModelForm):
    class Meta:
        model = SensorsData
        fields = ['pt2', 'ps2', 'Pbs2', 'Tbs2', 'HRs2', 'pt1', 'ps1', 'Pbs1', 'Tbs1', 'HRs1']
        widgets = {
            'pt2': forms.NumberInput(attrs={'class': 'form-control'}),
            'ps2': forms.NumberInput(attrs={'class': 'form-control'}),
            'Pbs2': forms.NumberInput(attrs={'class': 'form-control'}),
            'Tbs2': forms.NumberInput(attrs={'class': 'form-control'}),
            'HRs2': forms.NumberInput(attrs={'class': 'form-control'}),
            'pt1': forms.NumberInput(attrs={'class': 'form-control'}),
            'ps1': forms.NumberInput(attrs={'class': 'form-control'}),
            'Pbs1': forms.NumberInput(attrs={'class': 'form-control'}),
            'Tbs1': forms.NumberInput(attrs={'class': 'form-control'}),
            'HRs1': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SemaforoForm(forms.ModelForm):
    semaforo = forms.IntegerField(
        label="Intervalo de actualización (segundos)",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = IntervalosDeActualizacion
        fields = ['semaforo']
        
class SistemaForm(forms.ModelForm):
    sistema = forms.IntegerField(
        label="Intervalo de actualización (segundos)",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = IntervalosDeActualizacion
        fields = ['sistema']

class SimuladorForm(forms.ModelForm):
    class Meta:
        model = Simulador
        fields = ['insert_interval', 'estado']
        widgets = {
            'insert_interval': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
        }     


