from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.logger_config import logger_AFD
from django.utils import timezone
from datetime import datetime, timedelta
from applications.getdata.API.serializers import HistorialFieldSerializer
from applications.getdata.models import Historial


class GraficoDataView(APIView):
    def get(self, request, *args, **kwargs):
        tipo = request.GET.get("tipo")
        if not tipo:
            return Response({"error": "Debe especificar el campo 'tipo'"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validar 'tipo' usando metadatos del modelo (solo campos concretos)
        campos_validos = {f.name for f in Historial._meta.get_fields() if getattr(f, "concrete", False)}
        if tipo not in campos_validos:
            return Response({"error": f"Campo '{tipo}' no válido"},
                            status=status.HTTP_400_BAD_REQUEST)

        filtros = {f"{tipo}__isnull": False}

        tz = timezone.get_current_timezone()
        inicio = request.GET.get("inicio")
        fin = request.GET.get("fin")

        # inicio: yyyy-mm-dd a las 00:00:00 (aware)
        if inicio:
            try:
                dt_ini = timezone.make_aware(datetime.strptime(inicio, "%Y-%m-%d"), tz)
                filtros["ts__gte"] = dt_ini
            except ValueError:
                return Response({"error": "Fecha de inicio no válida. Formato: YYYY-MM-DD"},
                                status=status.HTTP_400_BAD_REQUEST)

        # fin inclusivo: yyyy-mm-dd 23:59:59 → implementado como < (fin + 1 día) 00:00:00
        if fin:
            try:
                dt_fin = timezone.make_aware(datetime.strptime(fin, "%Y-%m-%d"), tz) + timedelta(days=1)
                filtros["ts__lt"] = dt_fin
            except ValueError:
                return Response({"error": "Fecha de fin no válida. Formato: YYYY-MM-DD"},
                                status=status.HTTP_400_BAD_REQUEST)

        qs = Historial.objects.filter(**filtros).order_by("ts").values_list("ts", tipo)

        # Log para depuración
        logger_AFD.info(f"[GraficoDataView] filtros={filtros}")
        logger_AFD.info(f"[GraficoDataView] count={qs.count()}")

        # Construcción de ejes
        registros = list(qs)  # evalúa una sola vez
        labels = [ts.strftime("%Y-%m-%d %H:%M") for ts, _ in registros]
        valores = [round((valor or 0.0), 1) for _, valor in registros]

        logger_AFD.info(f"[GraficoDataView] labels={labels}")
        logger_AFD.info(f"[GraficoDataView] valores={valores}")

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
