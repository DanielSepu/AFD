from django.urls import path
from .views import *

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "settings"

urlpatterns = [
  path('settings/',settings,name='settings'),
  path('delete-project/<int:pk>/',ProjectDelete.as_view(),name='delete-project'),
  path('manager/', AdminPageView.as_view(), name='admin_page'),
  path('manager/config_semaforo/', ConfigSemaforoView.as_view(), name='config_semaforo'),
  path('manager/simulador/', SimuladorView.as_view(), name='simulador'),
  path('manager/rango_historial/', RangoHistorialView.as_view(), name='rango_historial'),
]

urlpatterns += staticfiles_urlpatterns()