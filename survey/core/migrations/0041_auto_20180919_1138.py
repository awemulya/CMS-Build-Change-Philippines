# Generated by Django 2.0 on 2018-09-19 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_constructionsubsteps_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='constructionsteps',
            name='name_de',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='constructionsteps',
            name='name_en',
            field=models.CharField(max_length=250, null=True),
        ),
    ]