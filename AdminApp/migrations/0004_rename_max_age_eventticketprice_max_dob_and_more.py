# Generated by Django 4.2.1 on 2024-05-12 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0003_alter_eventticketprice_max_age_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventticketprice',
            old_name='max_age',
            new_name='max_dob',
        ),
        migrations.RenameField(
            model_name='eventticketprice',
            old_name='min_age',
            new_name='min_dob',
        ),
    ]