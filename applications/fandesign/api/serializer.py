# serializers.py
from rest_framework import serializers
from .models import GraficoTolerancia

class GraficoToleranciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraficoTolerancia
        fields = ['tipo', 'tolerancia']
