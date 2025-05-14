from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from applications.getdata.models import SensorsData
from applications.settings.models import SemaforoEstado, FugasConfig
from modules.semaforo import Semaforo


class TestFugasV6(TestCase):
    def setUp(self):
        now = timezone.now()

        # Configuración
        FugasConfig.objects.create(
            presion_promedio=100,
            tolerancia_minima=0.05,
            tolerancia_maxima=0.2,
            alerta_activa=True
        )

        SemaforoEstado.objects.create(
            color_actual='verde',
            esta_bloqueado=False
        )

        # Registro hace 30 min (pt1 = 100)
        SensorsData.objects.create(
            ts=now - timedelta(minutes=30),
            pt1=100.0,
            pt2=488.0,
            ps2=271.0,
            Pbs2=95362.0,
            Tbs2=30.5,
            HRs2=34.5,
            ps1=490.0,
            Pbs1=95362.0,
            Tbs1=30.7,
            HRs1=37.2,
            k = 0,
            tbs = 0,
            hr = 0,
            tbh = 0,
            tgbh =0
        )

        # Registro actual (pt1 = 20)
        SensorsData.objects.create(
            ts=now,
            pt1=20.0,
            pt2=488.0,
            ps2=271.0,
            Pbs2=95362.0,
            Tbs2=30.5,
            HRs2=34.5,
            ps1=490.0,
            Pbs1=95362.0,
            Tbs1=30.7,
            HRs1=37.2,
            k = 0,
            tbs = 0,
            hr = 0,
            tbh = 0,
            tgbh = 0
        )

    def test_bloqueo_por_fuga_critica(self):
        semaforo = Semaforo()
        color = semaforo.fugas_v6()

        estado_actual = SemaforoEstado.objects.first()
        self.assertTrue(estado_actual.esta_bloqueado, "El semáforo debe estar bloqueado por fuga crítica.")
        self.assertEqual(estado_actual.color_actual, "rojo", "El semáforo debe estar en color rojo.")
        self.assertEqual(color, "rojo", "El color devuelto por fugas_v6 debe ser 'rojo'.")
