# Generated by Django 4.2.9 on 2024-02-05 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getdata', '0011_proyecto_factor'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='dis_e_sens',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='potencia',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
