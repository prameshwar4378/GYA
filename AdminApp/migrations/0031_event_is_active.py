# Generated by Django 4.2.1 on 2024-05-18 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0030_alter_event_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
