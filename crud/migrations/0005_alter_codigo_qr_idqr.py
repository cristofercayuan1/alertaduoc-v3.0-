# Generated by Django 5.0.4 on 2024-05-15 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0004_alter_codigo_qr_imagenqr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codigo_qr',
            name='idQr',
            field=models.CharField(max_length=6, primary_key=True, serialize=False),
        ),
    ]
