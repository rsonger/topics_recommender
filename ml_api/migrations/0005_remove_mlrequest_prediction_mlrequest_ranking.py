# Generated by Django 4.0.3 on 2022-04-30 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml_api', '0004_remove_abtest_created_by_remove_mlalgorithm_owner_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mlrequest',
            name='prediction',
        ),
        migrations.AddField(
            model_name='mlrequest',
            name='ranking',
            field=models.TextField(blank=True),
        ),
    ]
