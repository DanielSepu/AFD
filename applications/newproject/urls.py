from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "newproject"

urlpatterns = [
  path('newproject/',views.newproject,name="newproject"),
]

urlpatterns += staticfiles_urlpatterns()