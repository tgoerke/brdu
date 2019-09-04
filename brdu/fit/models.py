from django.db import models
from django import forms

# Validation
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

# CSV file handling
from .utils import unique_file_path
from .validators import ValidateCsv
from django.conf import settings
import os

# Plot handling
from django.contrib.sessions.models import Session

# Calculation Results
from jsonfield import JSONField

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

        # Make sure that the number of labeled cells is not greater than the overall number of cells.
        if self.number_of_labeled_cells is not None and self.number_of_all_cells is not None:
            if self.number_of_labeled_cells > self.number_of_all_cells:
                raise ValidationError({ # https://docs.djangoproject.com/en/2.2/ref/models/instances/#django.db.models.Model.clean
                    'number_of_labeled_cells': 'Ensure this value is less than or equal to the {:s}.'.format(self._meta.get_field('number_of_all_cells').verbose_name),
                    'number_of_all_cells': 'Ensure this value is greater than or equal to the {:s}.'.format(self._meta.get_field('number_of_labeled_cells').verbose_name)
                    })

class Upload(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    #user_filename = models.CharField(default='', max_length=255)
    file = models.FileField(upload_to=unique_file_path, validators=[ValidateCsv], max_length=255) # help_text='Upload your data in CSV format with <br /> column order as in the table on the left.') # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.FileField.upload_to; https://stackoverflow.com/questions/26575635/django-increase-filefield-length

class Assay(models.Model):
    """
    Holds all relevant values of a labeling assay for later reference like:
        - generated plot
        - estimated values (not implemented yet)
    """
    session = models.ForeignKey(Session, default='tfzs3e7d6x13029nvi88p9z7rhwwurcq', on_delete=models.CASCADE) # assay data is bound to a session and will be deleted together on removal of the session
    date_added = models.DateTimeField(auto_now_add=True) # Save date on creation of db entry.
    date_calculated = models.DateTimeField(auto_now=True) # Save date on change of db entry.
    experimental_data = JSONField(null=True)
    run_time = models.FloatField(null=True)
    calculation_results = JSONField(null=True) # https://stackoverflow.com/a/17970922/7192373
    plot = models.ImageField(upload_to=unique_file_path, max_length=255)

    @property
    def filename(self):
        return os.path.basename(self.plot.name)

    # https://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab

class SharedExperiment(Assay):
    """
    Holds permanently the cell cycle data for sharing with others.
    """
    date_shared = models.DateTimeField(auto_now_add=True)
    share_id = models.CharField(max_length=255)
    id_collision_count = models.IntegerField() # Counts collision until a unique id was found.
