# 
from rest_framework import serializers

class HistorialFieldSerializer(serializers.Serializer):
    name = serializers.CharField()
    verbose_name = serializers.CharField()
