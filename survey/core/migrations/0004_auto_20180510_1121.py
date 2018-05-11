# Generated by Django 2.0 on 2018-05-10 11:21

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20180506_0816'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='address',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='email_address',
            field=models.EmailField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='project/logo/'),
        ),
        migrations.AddField(
            model_name='project',
            name='organization',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='short_description',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='type',
            field=models.IntegerField(choices=[(0, 'First Type'), (1, 'Second Type'), (2, 'Third Type')], default=0),
        ),
        migrations.AddField(
            model_name='site',
            name='address',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='contact_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='site/photo/'),
        ),
        migrations.AddField(
            model_name='site',
            name='type',
            field=models.IntegerField(choices=[(0, 'First Type'), (1, 'Second Type'), (2, 'Third Type')], default=0),
        ),
    ]
