# Generated by Django 3.2.15 on 2023-08-02 16:53

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('server_securitate', '0015_auto_20230802_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 2, 16, 53, 4, 151964, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='dht',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 2, 16, 53, 4, 151746, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='pir',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 2, 16, 53, 4, 151205, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='requests',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 2, 16, 53, 4, 152450, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='usa',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 2, 16, 53, 4, 151507, tzinfo=utc)),
        ),
    ]
