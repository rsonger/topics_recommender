# Generated by Django 4.0.3 on 2022-03-18 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topics_recommender', '0002_topic_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
