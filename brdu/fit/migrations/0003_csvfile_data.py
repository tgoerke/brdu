# Generated by Django 2.2.2 on 2019-07-03 12:48

import django.core.validators
from django.db import migrations, models
import fit.utils


class Migration(migrations.Migration):

    dependencies = [
        ('fit', '0002_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='CsvFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_uploaded', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to=fit.utils.csv_file_path)),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurement_time', models.FloatField()),
                ('number_of_labeled_cells', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('number_of_all_cells', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'ordering': ('measurement_time',),
            },
        ),
    ]
