from django.shortcuts import render, redirect
import pandas as pd  # Importa pandas
import numpy as np
from django.http import HttpResponse
import requests as rq

from django.conf import settings

from applications.getdata.models import *
from .forms import *

def dbs(request):
   if request.method == 'GET':
      db_type = request.GET.get('type')
      print(db_type)
      if db_type == 'ventilador' or db_type is None:
         form = VentiladorForm() 
         context = {'db_type': db_type, 'form': form}
      
      if db_type == 'curva_diseno':
         form = CurvaDisenoForm() 
         context = {'db_type': db_type, 'form': form}
      
      if db_type == 'ducto':
         form = DuctoForm() 
         context = {'db_type': db_type, 'form': form}
      
      if db_type == 'equip_diesel':
         form = EquipDieselForm() 
         context = {'db_type': db_type, 'form': form}
      
      return render(request, 'dbs.html', context)



   if request.method == 'POST':
      form = VentiladorForm(request.POST)
      if form.is_valid():
            ventilador = form.save()
            return redirect('ventilador_detail', pk=ventilador.pk)


# def newvent(request):
#    if request.method == 'POST':
#       form = VentiladorForm(request.POST) # Bound form
#       if form.is_valid():
#             modelo = form.cleaned_data['modelo']
#             vmm = form.cleaned_data['vmm'] 
#             amm = form.cleaned_data['amm'] 
#             rmm = form.cleaned_data['rmm'] 
#             polos = form.cleaned_data['polos'] 
#             accesorios = form.cleaned_data['accesorios'] 
#             ventilador = Ventilador.objects.create(
#                modelo=modelo,
#                vmm=vmm,
#                amm=amm,
#                rmm=rmm,
#                polos=polos,
#                accesorios=accesorios
#             )
#       print("POST")
#       print(ventilador)
#       request.session['proyecto'] = Proyecto()

#    else:
#       form = VentiladorForm()

#    context = {'form': form}
#    return render(request, 'ventilador_form.html', context)


# def save_project(request):
#    if request.method == 'POST':
#       proyecto = request.session.get('proyecto') 
#       # Relacionar modelos        
#       proyecto.ventilador = Ventilador.objects.last()
#       proyecto.galeria = DimensionGaleria.objects.last()
#       # etc
#       proyecto.save()
#       # Redirigir a detail
#       print(proyecto)
#       return redirect('proyecto_detail', proyecto.id)