from django.urls import path

from applications.home.API.views import SemaforoApiView


urlpatterns = [
    path('v1/semaforo', SemaforoApiView.as_view(), name='semaforo'),
]