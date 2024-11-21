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
         context = {'setting_type': setting_type, 'form': form, 'equipamientos': EquipamientoDiesel.objects.all()}
      
         return render(request, 'settings.html', context)
      
      if setting_type == 'current_project':
         up = Proyecto.objects.all().order_by('-id').first()
         print(up)
         if up is not None:
            up_eqp = up.equipamientos.all()
            form = ProyectoForm(instance=up)
            context = {'setting_type': setting_type, 'form': form, 'id': up.id, 'up_eqp': up_eqp, 'equipamientos': EquipamientoDiesel.objects.all()}
         else:
            # Manejo de cuando no hay proyectos
            up_eqp = None
            form = ProyectoForm()

            context = {'exist':False,'setting_type': setting_type, 'form': form, 'up_eqp': up_eqp, 'equipamientos': EquipamientoDiesel.objects.all(), 'message': 'No hay proyectos disponibles.'}
         
         return render(request, 'settings.html', context)

   
   if request.method == 'POST':
      if setting_type == 'new_project':
         form = ProyectoForm(request.POST) 
         context = {'setting_type': setting_type, 'form': form}

         if form.is_valid():
            proyecto = form.save()
            proy = Proyecto.objects.get(id=proyecto.id)
            for k,v in enumerate(EquipamientoDiesel.objects.all()): #For para guardar foreing key desde checklist que fue creado a mano por style
               if request.POST.get('eq_'+str(v.id)):
                  proy.equipamientos.add(v)
            proy.save()
         else:
            print("Error el formulario no es valido")
            print(form.errors)
         return redirect('settings:settings')

      if setting_type == 'current_project':
         proy = Proyecto.objects.get(id=request.POST.get('id'))
         form = ProyectoForm(request.POST,instance=proy)

         if form.is_valid():
            form.save()
            proy.equipamientos.clear()
            for k,v in enumerate(EquipamientoDiesel.objects.all()): #Mismo For para foreing keys desde checklist con style no manejado por django
               if request.POST.get('eq_'+str(v.id)):
                  proy.equipamientos.add(v)
            proy.save()
         
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