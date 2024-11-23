from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "currentstatus"

urlpatterns = [
  path('currentstatus',views.currentstatus,name="currentstatus"),
  path('get_recent_data',views.get_recent_data,name="get_recent_data"),
  path('update_frequency',views.update_frequency,name="update_frequency"),
  path('excel_download',views.Excel,name="Excel"),
]

urlpatterns += staticfiles_urlpatterns()