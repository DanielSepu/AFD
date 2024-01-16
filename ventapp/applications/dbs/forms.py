from django import forms
from applications.getdata.models import Ventilador, CurvaDiseno, Ducto, EquipamientoDiesel

class VentiladorForm(forms.ModelForm):
   def clean_polos(self):
      polos = self.cleaned_data['polos']
      if polos % 2 != 0 or polos < 2:
         raise forms.ValidationError("Polos inválidos")
      return polos
   
   modelo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   polos = forms.IntegerField(widget=forms.Select(choices=[(2,'2'),(4,'4'),(6,'6'),(6,'6'),(8,'8'),(10,'10'),(12,'12')]))
   accesorios = forms.MultipleChoiceField(
      choices = [
                  ('rejilla_entrada','Rejilla Entrada'),('rejilla_salida','Rejilla Salida'),
                  ('silenciador_nucleo_entrada','Silenciador con núcleo entrada'),
                  ('silenciador_nucleo_salida','Silenciador con núcleo salida'),
                  ('silenciador_entrada','Silenciador entrada'), ('silenciador_salida','Silenciador salida'),
                  ('adaptador_ducto_ventilador','Adaptador ducto ventilador')],
      widget = forms.CheckboxSelectMultiple
   )

   class Meta:
      model = Ventilador
      fields = ['modelo', 'vmm', 'amm', 'rmm', 'polos', 'accesorios']
      labels = {
         'modelo':   'Modelo',
         'vmm':      'V',
         'amm':      'A',
         'rmm':      'R'}
      
class CurvaDisenoForm(forms.ModelForm):
   #Ventilador = forms.ModelMultipleChoiceField(queryset=Ventilador.objects.all())

   class Meta:
      model = CurvaDiseno
      fields = ['ventilador', 'angulo', 'rpm', 'densidad']
      labels = {
         'ventilador':   'Ventilador',
         'angulo':       'θ °',
         'rpm':          'RPM',
         'densidad':     'ρ (kg/m3)',}

class DuctoForm(forms.ModelForm):

   f_friccion = forms.FloatField(label='Factor de fricción (opcional)',required=False)
   f_fuga = forms.CharField(label='Factor de fuga (opcional)',required=False)

   class Meta:
      model = Ducto
      fields = ['t_ducto', 'f_friccion', 'f_fuga', 't_acople', 'largo']
      labels = {
         't_ducto':   'Tipo de ducto',
         't_acople':  'Tipo de acople',
         'largo':     'Largo ducto',
      }
      
class EquipDieselForm(forms.ModelForm):

   potencia = forms.FloatField(widget=forms.NumberInput(attrs={'onchange':'Funcion()'}),label='Potencia (HP)')
   qr_fabricante = forms.FloatField(label='Requerimiento de caudal informado de por el fabricante (opcional)',required=False)
   qr_calculado = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly','placeholder':''}),label='Requerimiento de caudal (m3/s)',)
   class Meta:
      model = EquipamientoDiesel
      fields = ['tipo','modelo_diesel','potencia','qr_fabricante','qr_calculado']
      labels = {
         'tipo':           'Tipo de equipamiento',
         'modelo_diesel':  'Modelo',
         'potencia':       'Potencia (HP)',
      }