# Generated by Django 4.2.9 on 2024-01-17 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getdata', '0003_caracteristicas_ventilador_tipo_equipamiento_diesel_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='curvadiseno',
            name='idu',
            field=models.CharField(default=''),
        ),
        migrations.AddField(
            model_name='ducto',
            name='idu',
            field=models.CharField(default=''),
        ),
        migrations.AddField(
            model_name='equipamientodiesel',
            name='idu',
            field=models.CharField(default=''),
        ),
        migrations.AddField(
            model_name='ventilador',
            name='idu',
            field=models.CharField(default=''),
        ),
    ]
