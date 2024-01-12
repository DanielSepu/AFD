from django import forms
from applications.getdata.models import Ventilador

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
      