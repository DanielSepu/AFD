from django.shortcuts import render, redirect, reverse
import pandas as pd  # Importa pandas
import numpy as np
from django.http import JsonResponse
from django.core import serializers
import json
#import requests as rq

from django.conf import settings

from applications.getdata.models import *
from applications.dbs.forms import *

def settings(request):
   setting_type = request.GET.get('type')
   print(setting_type)
   print(request.method)
   if request.method == 'GET':
      if setting_type == 'new_project' or setting_type is None:
         form = ProyectoForm()
         context = {'setting_type': setting_type, 'form': form}
      
         return render(request, 'settings.html', context)
      
      if setting_type == 'current_project':
         up = Proyecto.objects.all().order_by('-id').first()
         print(up)
         form = ProyectoForm(instance=up)
         context = {'setting_type': setting_type, 'form': form, 'id': up.id}
         return render(request, 'settings.html', context)

   
   if request.method == 'POST':
      if setting_type == 'new_project':
         form = ProyectoForm(request.POST) 
         context = {'setting_type': setting_type, 'form': form}
         if form.is_valid():
            proyecto = form.save()
         
         return redirect('settings')
         #return render(request, 'settings.html', context)

      if setting_type == 'current_project':
         proy = Proyecto.objects.get(id=request.POST.get('id'))
         form = ProyectoForm(request.POST,instance=proy)
         if form.is_valid():
            form.save()
         
         return redirect(reverse('settings:settings') + '?type=current_project')

      if setting_type == 'new_project_2':
         task=request.POST.get('task')
         cd = CurvaDiseno.objects.filter(ventilador_id=task)
         cdpk = json.loads(serializers.serialize('json', cd, fields=("id", "idu")))
         return JsonResponse({'cdpk':cdpk})
      
      if setting_type == 'new_project_3':
         task=request.POST.getlist('task[]')
         sumatoria = 0
         for i in task:
            eq = EquipamientoDiesel.objects.get(id=i)
            sumatoria += eq.qr_calculado
         return JsonResponse({'sumatoria':sumatoria})



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