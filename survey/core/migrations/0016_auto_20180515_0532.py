# Generated by Django 2.0 on 2018-05-15 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20180515_0531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklist',
            name='text_en',
        ),
        migrations.RemoveField(
            model_name='step',
            name='name_en',
        ),
        migrations.AlterField(
            model_name='setting',
            name='local_language',
            field=models.CharField(blank=True, choices=[('de', 'German')], max_length=2, null=True),
        ),
    ]
