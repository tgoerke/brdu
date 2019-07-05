# Generated by Django 2.2.2 on 2019-07-03 15:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fit', '0005_csvfile_user_filename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csvfile',
            name='user_filename',
            field=models.CharField(default='', max_length=3, validators=[django.core.validators.MaxLengthValidator(3)]),
        ),
    ]