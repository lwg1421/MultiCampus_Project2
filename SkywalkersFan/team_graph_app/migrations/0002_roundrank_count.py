# Generated by Django 4.1.1 on 2022-10-26 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_graph_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='roundrank_count',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('round1', models.IntegerField()),
                ('round2', models.IntegerField()),
                ('round3', models.IntegerField()),
                ('round4', models.IntegerField()),
                ('round5', models.IntegerField()),
                ('round6', models.IntegerField()),
            ],
        ),
    ]
