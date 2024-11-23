from django.urls import path
from . import views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "settings"

urlpatterns = [
  path('settings/',views.settings,name='settings'),
  path('delete-project/<int:pk>/',views.ProjectDelete.as_view(),name='delete-project'),
]

urlpatterns += staticfiles_urlpatterns()