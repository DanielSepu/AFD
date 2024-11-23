from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "dbs"

urlpatterns = [
  path('dbs/',views.dbs,name="dbs"),
  path('dbs/create-caracteristica',views.CaracteristicasVentiladorView.as_view(),name="create-caracteristica"),
  path('edit-curva-diseno/<int:pk>/',views.CurvaDisenoEditView.as_view(),name="edit-curva-diseno"),
  path('edit-ducto/<int:pk>/',views.DuctoEditView.as_view(),name="edit-ducto"),
  path('edit-sistema-partida/<int:pk>/',views.SistemaPartidaEditView.as_view(),name="edit-sistema-partida"),
  path('edit-ventilador/<int:pk>/',views.VentiladorEditView.as_view(),name="edit-ventilador"),
  path('edit-equipamiento/<int:pk>/',views.VentiladorEditView.as_view(),name="edit-equipamiento"),
]

urlpatterns += staticfiles_urlpatterns()