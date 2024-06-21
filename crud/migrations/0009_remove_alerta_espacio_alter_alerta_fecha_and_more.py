# Generated by Django 5.0.4 on 2024-05-25 15:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0008_remove_alerta_evidencia_alerta_espacio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alerta',
            name='espacio',
        ),
        migrations.AlterField(
            model_name='alerta',
            name='fecha',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='alerta',
            name='idAlerta',
            field=models.CharField(max_length=6, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='espacio',
            name='idEspacio',
            field=models.CharField(editable=False, max_length=3, primary_key=True, serialize=False, unique=True),
        ),
        migrations.CreateModel(
            name='SolucionAlerta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_resolucion', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.CharField(max_length=100)),
                ('evidencia1', models.ImageField(upload_to='evidencias_solucion')),
                ('evidencia2', models.ImageField(upload_to='evidencias_solucion')),
                ('evidencia3', models.ImageField(blank=True, null=True, upload_to='evidencias_solucion')),
                ('alerta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='crud.alerta')),
            ],
        ),
    ]
