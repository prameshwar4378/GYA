# Generated by Django 4.2.1 on 2024-05-15 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0017_alter_guest_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='member_id',
            field=models.CharField(default=0, max_length=20, null=True, unique=True),
        ),
    ]
