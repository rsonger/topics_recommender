# Generated by Django 4.0.3 on 2022-05-25 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml_api', '0010_mlalgorithm_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlalgorithm',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='mltestingstatus',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
