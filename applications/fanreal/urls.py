from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "fanreal"

urlpatterns = [
  path('fanreal',views.fanreal,name="fanreal"),
]

urlpatterns += staticfiles_urlpatterns()