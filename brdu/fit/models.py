from django.db import models
from django import forms

# Validation
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

# CSV file handling
from .utils import unique_file_path
from .validators import ValidateFileType
from django.conf import settings
import os

# Plot handling
from django.contrib.sessions.models import Session

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
    measurement_time = models.FloatField(validators=[MinValueValidator(0)])
    number_of_labeled_cells = models.IntegerField(validators=[MinValueValidator(0)])
    number_of_all_cells = models.IntegerField(validators=[MinValueValidator(0)])
    class Meta:
        ordering = ('measurement_time',)
    
    def clean(self):
        # Do validation that requires access to more than a single field.

        # Make sure that number of labeled cells is not greater than overall cell number.
        if self.number_of_labeled_cells is not None and self.number_of_all_cells is not None:
            if self.number_of_labeled_cells > self.number_of_all_cells:
                raise ValidationError({'number_of_all_cells': 'Ensure this value is greater than or equal to the number of labeled cells.'}) # https://docs.djangoproject.com/en/2.2/ref/models/instances/#django.db.models.Model.clean

class Upload(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    #user_filename = models.CharField(default='', max_length=255)
    file = models.FileField(upload_to=unique_file_path, validators=[ValidateFileType]) # FileExtensionValidator(['csv']); help_text='Upload your data in CSV format with <br /> column order as in the table on the left.') # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.FileField.upload_to

class Assay(models.Model):
    """
    Holds all relevant values of a labeling assay for later reference like:
        - generated plot
        - estimated values (not implemented yet)
    """
    date_added = models.DateTimeField(auto_now_add=True)
    plot = models.ImageField(upload_to=unique_file_path)
    session = models.ForeignKey(Session, default='tfzs3e7d6x13029nvi88p9z7rhwwurcq', on_delete=models.CASCADE) # assay data is bound to a session and will be deleted together on removal of the session

    @property
    def filename(self):
        return os.path.basename(self.plot.name)

    # https://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab