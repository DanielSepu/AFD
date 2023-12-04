from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "currentstatus"

urlpatterns = [
  path('currentstatus',views.currentstatus,name="currentstatus"),
]

urlpatterns += staticfiles_urlpatterns()