# Generated by Django 4.2.9 on 2024-01-16 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getdata', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ducto',
            name='tipo',
        ),
        migrations.AddField(
            model_name='ducto',
            name='t_acople',
            field=models.CharField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ducto',
            name='t_ducto',
            field=models.CharField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ducto',
            name='f_fuga',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='equipamientodiesel',
            name='modelo_diesel',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='equipamientodiesel',
            name='tipo',
            field=models.CharField(),
        ),
    ]
