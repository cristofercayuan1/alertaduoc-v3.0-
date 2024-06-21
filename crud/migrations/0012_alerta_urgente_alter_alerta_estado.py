# Generated by Django 5.0.4 on 2024-06-05 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0011_alter_alerta_evidencia1_alter_alerta_evidencia2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='alerta',
            name='urgente',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alerta',
            name='estado',
            field=models.CharField(choices=[('1', 'Pendiente'), ('2', 'Resuelto'), ('3', 'En observación')], default='1', max_length=1),
        ),
    ]