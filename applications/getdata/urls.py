from django.urls import path

from applications.getdata.API.views import GraficoDataView, HistorialFieldsView
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "getdata"

urlpatterns = [
  path('getdata',views.getdata,name="getdata"),
  path("api/grafico/", GraficoDataView.as_view(), name="api-grafico"),
  path('api/historial/fields/', HistorialFieldsView.as_view(), name='historial-fields'),
    
]

urlpatterns += staticfiles_urlpatterns()