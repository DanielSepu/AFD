from django import forms
from .models import FugasConfig, SemaforoEstado

class FugasConfigForm(forms.ModelForm):
    class Meta:
        model = FugasConfig
        fields = ['presion_promedio', 'tolerancia_minima', 'tolerancia_maxima', 'alerta_activa']
        labels = {
            'presion_promedio': 'Presión promedio (Pa)',
            'tolerancia_minima': 'Tolerancia mínima %',
            'tolerancia_maxima': 'Tolerancia máxima %',
            'alerta_activa': 'Alerta activa',
        }
        widgets = {
            'presion_promedio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tolerancia_minima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tolerancia_maxima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class SemaforoEstadoForm(forms.ModelForm):
    class Meta:
        model = SemaforoEstado
        fields = ['color_actual', 'esta_bloqueado', 'motivo_bloqueo']
        widgets = {
            'color_actual': forms.Select(attrs={'class': 'form-select'}),
            'motivo_bloqueo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
