from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "currentstatus"

urlpatterns = [
  path('currentstatus',views.currentstatus,name="currentstatus"),
  path('get_recent_data',views.get_recent_data,name="get_recent_data"),
]

urlpatterns += staticfiles_urlpatterns()