# Generated by Django 5.0.2 on 2024-03-23 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sync_model', '0003_synctask_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockaction',
            name='stock_number',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
