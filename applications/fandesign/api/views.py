# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from applications.fandesign.models import GraficoTolerancia


class ToleranciaGraficoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo = request.query_params.get('tipo')
        if not tipo:
            return Response({"error": "Falta el parámetro 'tipo'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tolerancia = GraficoTolerancia.objects.get(tipo=tipo, usuario=request.user)
            return Response({
                "tipo": tipo,
                "tolerancia": tolerancia.tolerancia
            })
        except GraficoTolerancia.DoesNotExist:
            return Response({
                "tipo": tipo,
                "tolerancia": "AN3"  # valor por defecto
            })

    def post(self, request):
        tipo = request.data.get('tipo')
        valor = request.data.get('tolerancia')

        if not tipo or not valor:
            return Response({"error": "Faltan datos."}, status=status.HTTP_400_BAD_REQUEST)

        tolerancia_obj, created = GraficoTolerancia.objects.get_or_create(
            tipo=tipo
        )
        tolerancia_obj.tolerancia = valor
        tolerancia_obj.save()

        return Response({
            "status": "ok",
            "tipo": tipo,
            "tolerancia": valor,
            "created": created
        }, status=status.HTTP_200_OK)
