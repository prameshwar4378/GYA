# Generated by Django 4.2.1 on 2024-05-18 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0034_videogallery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='booking_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]