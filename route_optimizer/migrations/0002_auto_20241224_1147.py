# Generated by Django 3.2.23 on 2024-12-24 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route_optimizer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelstation',
            name='opis_truckstop_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='fuelstation',
            name='rack_id',
            field=models.IntegerField(default=0),
        ),
    ]
