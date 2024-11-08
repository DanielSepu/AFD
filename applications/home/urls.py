from django.urls import path

from applications.home.views import *
from applications.home.API.urls import *

urlpatterns += [
    path('', HomeView.as_view(), name='homepage'),
]