from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "dbs"

urlpatterns = [
  path('dbs/',views.dbs,name="dbs"),
]

urlpatterns += staticfiles_urlpatterns()