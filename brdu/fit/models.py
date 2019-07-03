from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms

# CSV file handling
from .utils import csv_file_path
from django.core.validators import MaxLengthValidator

# Debugging
from IPython import embed

class Experiments(models.Model):
    # experiment title
    title = models.CharField(max_length=255, null=False)
    labeling_fraction = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{} - {}".format(self.title, self.labeling_fraction)

class File(models.Model):
    file = models.FileField(blank=False, null=False)
    remark = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

class Data(models.Model):
    # created = models.DateTimeField(auto_now_add=True)
    #measurement_time = models.CharField(max_length=100, blank=True, default='')
    measurement_time = models.FloatField()
    number_of_labeled_cells = models.IntegerField(validators=[MinValueValidator(0)])
    number_of_all_cells = models.IntegerField(validators=[MinValueValidator(0)])
    class Meta:
        ordering = ('measurement_time',)

class CsvFile(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    user_filename = models.CharField(default='', max_length=255)
    file = models.FileField(upload_to=csv_file_path) # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.FileField.upload_to
