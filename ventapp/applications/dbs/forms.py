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
   
   modelo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   polos = forms.IntegerField(widget=forms.Select(choices=[(2,'2'),(4,'4'),(6,'6'),(6,'6'),(8,'8'),(10,'10'),(12,'12')]))
   accesorios = CustomMMCF(queryset=Caracteristicas_Ventilador.objects.all(),widget=forms.CheckboxSelectMultiple,label='Accesorios')

   class Meta:
      model = Ventilador
      fields = ['idu', 'modelo', 'vmm', 'amm', 'rmm', 'polos', 'accesorios']
      labels = {
         'idu': 'ID',
         'modelo':   'Modelo',
         'vmm':      'V',
         'amm':      'A',
         'rmm':      'R'}
      
class CurvaDisenoForm(forms.ModelForm):
   ventilador = CustomMCF(queryset=Ventilador.objects.all())

   class Meta:
      model = CurvaDiseno
      fields = ['idu', 'ventilador', 'angulo', 'rpm', 'densidad']
      labels = {
         'idu': 'ID',
         'angulo':       'θ °',
         'rpm':          'RPM',
         'densidad':     'ρ (kg/m3)',}

class DuctoForm(forms.ModelForm):

   f_friccion = forms.FloatField(label='Factor de fricción (opcional)',required=False)
   f_fuga = forms.CharField(label='Factor de fuga (opcional)',required=False)

   class Meta:
      model = Ducto
      fields = ['idu', 't_ducto','f_friccion', 'f_fuga', 't_acople', 'largo']
      labels = {
         'idu': 'ID',
         't_ducto':   'Tipo de ducto',
         't_acople':  'Tipo de acople',
         'largo':     'Largo ducto',
      }
      
class EquipDieselForm(forms.ModelForm):
   
   class CustomEDN(forms.ModelChoiceField):
      def label_from_instance(self, obj):
         return obj.nombre

   potencia = forms.FloatField(widget=forms.NumberInput(attrs={'onchange':'Funcion()','value':'0'}),label='Potencia (HP)')
   qr_fabricante = forms.FloatField(widget=forms.NumberInput(attrs={'onchange':'Funcion2()'}),label='Requerimiento de caudal informado de por el fabricante (opcional)',required=False)
   qr_calculado = forms.FloatField(widget=forms.NumberInput(attrs={'readonly':'readonly','placeholder':''}),label='Requerimiento de caudal (m3/s)',)
   tipo = CustomEDN(queryset=Tipo_Equipamiento_Diesel.objects.all(),label='Tipo de equipamiento')
   
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
         return obj.modelo +' | '+ obj.idu
   class CustomPFI(forms.ModelChoiceField):
      def label_from_instance(self, obj):
         return obj.idu
      
   class CustomPMMCF(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
         return obj.modelo_diesel +' | '+ obj.idu

   ventilador = CustomPFV(queryset=Ventilador.objects.all(),widget=forms.Select,label='Ventilador')
   curva_diseno = forms.MultipleChoiceField(label="Curva Diseño",widget=forms.Select(attrs={'disabled':'disabled'}))#CustomPFI(queryset=CurvaDiseno.objects.all(),widget=forms.Select,label='Curva Diseño')
   ducto = CustomPFI(queryset=Ducto.objects.all(),widget=forms.Select,label='Ducto')
   s_partida = CustomMMCF(queryset=Sistema_Partida.objects.all(),widget=forms.Select,label='Sistema de partida')
   equipamientos = CustomPMMCF(queryset=EquipamientoDiesel.objects.all(),label='Equipamientos')

   class Meta:
      model = Proyecto
      fields = ['ventilador','curva_diseno','ducto','equipamientos','caudal_requerido','codos','ancho_galeria','alto_galeria','area_galeria','s_partida']
      labels = {
         
      }