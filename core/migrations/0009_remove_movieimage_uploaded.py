# Generated by Django 2.1.7 on 2019-04-06 00:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20190405_2219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movieimage',
            name='uploaded',
        ),
    ]
