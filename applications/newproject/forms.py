from django import forms

class VentiladorForm(forms.Form):
   modelo = forms.CharField()
   vmm = forms.FloatField()
   amm = forms.FloatField()
   rmm = forms.FloatField()
   polos = forms.IntegerField()
   accesorios = forms.CharField()