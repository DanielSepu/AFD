# Generated by Django 4.2.11 on 2024-10-10 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getdata', '0014_alter_ducto_f_fuga'),
    ]

    operations = [
        migrations.AddField(
            model_name='caracteristicas_ventilador',
            name='perdida_choque',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
