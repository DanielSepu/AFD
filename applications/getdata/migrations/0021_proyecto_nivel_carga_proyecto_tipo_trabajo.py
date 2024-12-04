# Generated by Django 4.2.11 on 2024-10-30 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getdata', '0020_proyecto_lf_evento'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='nivel_carga',
            field=models.CharField(choices=[('liviana', 'Liviana'), ('moderada', 'Moderada'), ('pesada', 'Pesada')], default='liviana', max_length=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='tipo_trabajo',
            field=models.CharField(choices=[('trabajo continuo', 'Trabajo continuo'), ('75-25', '75% trabajo - 25%'), ('50-50', '50% trabajo - 50%'), ('25-75', '25% trabajo - 75%')], default='trabajo continuo', max_length=16),
            preserve_default=False,
        ),
    ]
