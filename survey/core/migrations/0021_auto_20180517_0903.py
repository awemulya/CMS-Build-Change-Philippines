# Generated by Django 2.0 on 2018-05-17 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20180515_0846'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='step',
            options={'ordering': ['order']},
        ),
    ]
