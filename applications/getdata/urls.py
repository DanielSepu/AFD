from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "getdata"

urlpatterns = [
  path('getdata',views.getdata,name="getdata"),
    
]

urlpatterns += staticfiles_urlpatterns()