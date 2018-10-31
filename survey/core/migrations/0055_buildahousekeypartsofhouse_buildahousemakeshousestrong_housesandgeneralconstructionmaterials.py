# Generated by Django 2.0 on 2018-10-31 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_badphoto_goodphoto'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildAHouseKeyPartsOfHouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('good_photo', models.ImageField(blank=True, null=True, upload_to='BuildAHouse/KeyPartsOfHouse/good_photo/')),
                ('good_photo_desc', models.TextField(blank=True, null=True)),
                ('bad_photo', models.ImageField(blank=True, null=True, upload_to='BuildAHouse/KeyPartsOfHouse/bad_photo/')),
                ('bad_photo_desc', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuildAHouseMakesHouseStrong',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('pdf', models.FileField(blank=True, null=True, upload_to='BuildAHouseMakesHouseStrong/pdf/')),
            ],
        ),
        migrations.CreateModel(
            name='HousesAndGeneralConstructionMaterials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('good_photo', models.ImageField(blank=True, null=True, upload_to='HousesAndGeneralConstruction/materials/good_photo/')),
                ('good_photo_desc', models.TextField(blank=True, null=True)),
                ('bad_photo', models.ImageField(blank=True, null=True, upload_to='HousesAndGeneralConstruction/materials/bad_photo/')),
                ('bad_photo_desc', models.TextField(blank=True, null=True)),
            ],
        ),
    ]