# Generated by Django 3.2.15 on 2023-07-29 15:51

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('server_securitate', '0013_auto_20230729_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 29, 15, 51, 59, 347432, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='dht',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 29, 15, 51, 59, 347202, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='pir',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 29, 15, 51, 59, 346624, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='requests',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 29, 15, 51, 59, 347920, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='usa',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 29, 15, 51, 59, 346982, tzinfo=utc)),
        ),
    ]
