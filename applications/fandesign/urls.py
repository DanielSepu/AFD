from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "fandesign"

urlpatterns = [
  path('fandesign/',views.fandesign,name="fandesign"),
]

urlpatterns += staticfiles_urlpatterns()