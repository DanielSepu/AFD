from django.urls import path

from applications.fandesign.api.views import ToleranciaGraficoView

from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "fandesign"

urlpatterns = [
  # path('fandesign/',views.fandesign,name="fandesign"),
  path('fandesign/',views.FanDesignView.as_view() ,name="fandesign"),
  path('api/tolerancia/', ToleranciaGraficoView.as_view(), name='actualizar-tolerancia'),
]

urlpatterns += staticfiles_urlpatterns()