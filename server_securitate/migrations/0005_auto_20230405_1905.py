# Generated by Django 3.2.15 on 2023-04-05 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_securitate', '0004_auto_20230322_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='dht',
            name='user',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AddField(
            model_name='pir',
            name='user',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AddField(
            model_name='usa',
            name='user',
            field=models.CharField(default='', max_length=60),
        ),
    ]
