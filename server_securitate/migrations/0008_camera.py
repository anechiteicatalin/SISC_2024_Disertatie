# Generated by Django 3.2.15 on 2023-06-14 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_securitate', '0007_auto_20230426_2055'),
    ]

    operations = [
        migrations.CreateModel(
            name='CAMERA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Camera', max_length=50)),
                ('mac', models.CharField(max_length=20)),
                ('user', models.CharField(default='', max_length=60)),
                ('uid', models.IntegerField(default=0)),
                ('socket', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField()),
            ],
        ),
    ]