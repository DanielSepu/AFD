# Generated by Django 4.2.11 on 2024-10-16 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getdata', '0018_rename_perdida_choque_caracteristicas_ventilador_factor_choque'),
    ]

    operations = [
        migrations.AddField(
            model_name='ducto',
            name='area',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ducto',
            name='diametro',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ducto',
            name='t_ducto',
            field=models.CharField(choices=[('circular', 'Circular'), ('ovalado', 'Ovalado')], max_length=10),
        ),
        migrations.AlterField(
            model_name='ventilador',
            name='img_ventilador',
            field=models.ImageField(default='ventilador/vent-def.png', upload_to='ventilador/'),
        ),
    ]
