# Generated by Django 4.0.3 on 2022-06-30 01:46

from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('topics_recommender', '0006_usersession_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='description',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='short_description',
        ),
        migrations.CreateModel(
            name='TopicTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('short_description', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='topics_recommender.topic')),
            ],
            options={
                'verbose_name': 'topic Translation',
                'db_table': 'topics_recommender_topic_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatableModel, models.Model),
        ),
    ]
