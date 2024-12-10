from django import forms
from .models import Sistema_Partida

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

