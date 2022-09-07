# Generated by Django 4.0.3 on 2022-09-06 04:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topics_recommender', '0008_alter_usersession_options'),
        ('survey_tasks', '0005_alter_cttresponse_user_session_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommenderResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now=True)),
                ('topic1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice1', to='topics_recommender.topic')),
                ('topic2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice2', to='topics_recommender.topic')),
                ('topic3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice3', to='topics_recommender.topic')),
                ('user_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topics_recommender.usersession')),
            ],
        ),
    ]