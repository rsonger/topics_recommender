# Generated by Django 4.0.3 on 2022-04-28 00:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Endpoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('owner', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MLAlgorithm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('code', models.TextField()),
                ('version', models.CharField(max_length=128)),
                ('owner', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent_endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ml_api.endpoint')),
            ],
            options={
                'verbose_name': 'ML algorithm',
            },
        ),
        migrations.CreateModel(
            name='MLRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_data', models.TextField()),
                ('full_response', models.TextField()),
                ('response', models.CharField(max_length=32)),
                ('prediction', models.CharField(max_length=64, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent_mlalgorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ml_api.mlalgorithm')),
            ],
            options={
                'verbose_name': 'ML request',
            },
        ),
        migrations.CreateModel(
            name='MLAlgorithmStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=16)),
                ('active', models.BooleanField()),
                ('created_by', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent_mlalgorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='ml_api.mlalgorithm', verbose_name='parent ML algorithm')),
            ],
            options={
                'verbose_name': 'ML algorithm status',
                'verbose_name_plural': 'ML algorithm statuses',
            },
        ),
        migrations.CreateModel(
            name='ABTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('created_by', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('summary', models.TextField(blank=True)),
                ('algorithm_A', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='algorithm_A', to='ml_api.mlalgorithm')),
                ('algorithm_B', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='algorithm_B', to='ml_api.mlalgorithm')),
            ],
            options={
                'verbose_name': 'A/B Test',
            },
        ),
    ]
