# Generated by Django 5.0.6 on 2024-06-21 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0016_alter_alerta_descripcion'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='foto_perfil',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]