from django.urls import path

from applications.home.views import *


urlpatterns = [
    path('', HomeView.as_view(), name='homepage'),
]