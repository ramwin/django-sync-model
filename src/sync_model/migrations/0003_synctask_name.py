# Generated by Django 5.0.2 on 2024-03-20 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sync_model', '0002_synctask_source_db_synctask_target_db'),
    ]

    operations = [
        migrations.AddField(
            model_name='synctask',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]
