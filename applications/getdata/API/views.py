from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from applications.getdata.API.serializers import HistorialFieldSerializer
from applications.getdata.models import Historial


class GraficoDataView(APIView):
    def get(self, request, *args, **kwargs):
        tipo = request.GET.get("tipo")
        if not tipo:
            return Response({"error": "Debe especificar el campo 'tipo'"}, status=status.HTTP_400_BAD_REQUEST)

        if not hasattr(Historial, tipo):
            return Response({"error": f"Campo '{tipo}' no válido"}, status=status.HTTP_400_BAD_REQUEST)

        # Filtros dinámicos
        filtros = {f"{tipo}__isnull": False}
        inicio = request.GET.get("inicio")
        fin = request.GET.get("fin")

        if inicio:
            try:
                filtros["ts__gte"] = datetime.strptime(inicio, "%Y-%m-%d")
            except ValueError:
                return Response({"error": "Fecha de inicio no válida"}, status=status.HTTP_400_BAD_REQUEST)

        if fin:
            try:
                filtros["ts__lte"] = datetime.strptime(fin, "%Y-%m-%d")
            except ValueError:
                return Response({"error": "Fecha de fin no válida"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Historial.objects.filter(**filtros).order_by("ts").values_list("ts", tipo)

        labels = [ts.strftime("%b %d") for ts, _ in queryset]
        valores = [round(valor,1) for _, valor in queryset]
       
        return Response({
            "labels": labels,
            "data": valores,
            "label": tipo.replace("_", " ").capitalize()
        })


class HistorialFieldsView(APIView):
    """
    GET /api/historial/fields/
    Devuelve lista de { name, verbose_name } de los campos del modelo Historial.
    """
    def get(self, request, *args, **kwargs):
        # Reemplaza 'tu_app' por el nombre real de tu aplicación

        fields = []
        for f in Historial._meta.get_fields():
            # Solo los campos de base de datos que tienen verbose_name
            if hasattr(f, 'verbose_name'):
                fields.append({
                    'name': f.name,
                    'verbose_name': str(f.verbose_name)
                })
        serializer = HistorialFieldSerializer(fields, many=True)
        return Response(serializer.data)
