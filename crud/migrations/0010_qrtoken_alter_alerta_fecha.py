# Generated by Django 5.0.4 on 2024-05-25 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0009_remove_alerta_espacio_alter_alerta_fecha_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QrToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=36, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='alerta',
            name='fecha',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
