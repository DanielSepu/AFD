import pdb
from django.forms import BaseModelForm
from django.shortcuts import render, redirect
import pandas as pd  # Importa pandas
import numpy as np
from django.http import HttpResponse
import requests as rq

from django.conf import settings
from django.contrib import messages
from django.views.generic import UpdateView, CreateView

from applications.getdata.models import *
from .forms import *

def dbs(request):
   if request.method == 'GET':
      db_type = request.GET.get('type')
      print(db_type)
      #from applications.getdata.models import Ventilador
      #v1 = Ventilador.objects.get(id=3)
      #print(v1.accesorios.all().values())

      if db_type == 'ventilador' or db_type is None:
         form = VentiladorForm() 
         context = {'db_type': db_type, 'form': form}
         return render(request, 'widgets/dbs/ventilador.html', context)
      
      if db_type == 'curva_diseno':
         form = CurvaDisenoForm() 
         context = {'db_type': db_type, 'form': form}
         return render(request, 'widgets/dbs/curvaDiseno.html', context)
      
      if db_type == 'ducto':
         form = DuctoForm(ocultar=False)
         context = {'db_type': db_type, 'form': form}
         return render(request, 'widgets/dbs/ducto.html', context)
      
      if db_type == 'equip_diesel':
         form = EquipDieselForm() 
         context = {'db_type': db_type, 'form': form}
         return render(request, 'widgets/dbs/equipDiesel.html', context)
      
      return render(request, 'dbs.html', context)



   if request.method == 'POST':
      db_type = request.GET.get('type')
      #for k, v in request.POST.items():
         #print('['+k+']: '+v)
      
      """Obtener queryset desde el form que viene"""
      #l = VentiladorForm(request.POST) 
      #if l.is_valid(): #Si no se usa is valid, cleaned_data no funciona
         #print(l.cleaned_data.get("accesorios"))
   
      if db_type == 'ventilador' or db_type is None:
         form = VentiladorForm(request.POST) 
         context = {'db_type': db_type, 'form': form}
         if form.is_valid():
            ventilador = form.save()
            #return redirect('ventilador_detail', pk=ventilador.pk)
            messages.success(request,"Se ha guardado el nuevo ventilador")
         else:
            print(f"guardar el ventilador no es valido")
            print(form.errors)
      
      if db_type == 'curva_diseno':
         form = CurvaDisenoForm(request.POST) 
         context = {'db_type': db_type, 'form': form}
         
         caudal = []
         presion = []
         power = []

         if form.is_valid():
            #cppL = []
            for x in range(int(request.POST.get('veces'))):
               
               caudal.append( float(request.POST.get('caudal_'+str(x)) )) 
               presion.append( float(request.POST.get('presion_'+str(x)) )) 
               power.append( float(request.POST.get('power_'+str(x)) )) 
               
               #cppL.append(cpp)

            json_data = { 
               "presion": presion ,
               "caudal" : caudal,
               "potencia" : power
            }


            curva = form.save(commit=False)
            curva.datos_curva = json_data
            curva.save()
         else:
            print(f"guardar la curva de diseño no es valido")
            print(form.errors)
      
      if db_type == 'ducto':
         form = DuctoForm(request.POST) 
         context = {'db_type': db_type, 'form': form}
         if form.is_valid():
            ducto = form.save()
         else:
            print(f"guardar el ducto no es valido")
            print(form.errors)
      
      if db_type == 'equip_diesel':
         form = EquipDieselForm(request.POST) 
         context = {'db_type': db_type, 'form': form}
         if form.is_valid():
            equipod = form.save()
         else:
            print(f"guardar el equipo diesel no es valido")
            print(form.errors)
         
      return redirect('/dbs/?type=ventilador')

class CaracteristicasVentiladorView(CreateView):
   model = Caracteristicas_Ventilador 
   form_class = Caracteristicas_VentiladorForm
   template_name = 'widgets/dbs/createCaracteristicaVentilador.html'
   success_url = '/'


class CurvaDisenoEditView(UpdateView):
   model = CurvaDiseno
   form_class = CurvaDisenoForm 
   template_name = 'widgets/dbs/edit.html' 
   success_url = '/'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['db_type'] = 'Curva caracteristica ventilador'
      return context


class DuctoEditView(UpdateView):
   model = Ducto
   form_class = DuctoForm
   template_name = 'widgets/dbs/edit.html' 
   success_url = '/'

   def form_valid(self, form) :
      print(self.request.POST)
      return super().form_valid(form)

   

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['db_type'] = 'Ducto'
      return context
   
class SistemaPartidaEditView(UpdateView):
   model = Sistema_Partida
   form_class = SistemaPartidaForm 
   template_name = 'widgets/dbs/edit.html' 
   success_url = '/'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['db_type'] = 'Sistema de partida'
      return context
   
class VentiladorEditView(UpdateView):
   model = Ventilador
   form_class = VentiladorForm 
   template_name = 'widgets/dbs/edit.html' 
   success_url = '/'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['db_type'] = 'Ventilador'
      return context
   
class EquipamientoEditView(UpdateView):
   model = EquipamientoDiesel
   form_class = EquipDieselForm 
   template_name = 'widgets/dbs/edit.html' 
   success_url = '/'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['db_type'] = 'Equipamiento diesel'
      return context
   

