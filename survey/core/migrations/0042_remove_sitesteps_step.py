# Generated by Django 2.0 on 2018-09-19 02:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20180919_0226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitesteps',
            name='step',
        ),
    ]