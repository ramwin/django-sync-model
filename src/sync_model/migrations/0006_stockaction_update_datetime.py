# Generated by Django 5.0.2 on 2024-03-23 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sync_model', '0005_stockaction_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockaction',
            name='update_datetime',
            field=models.DateTimeField(null=True),
        ),
    ]