import uuid
import os
from django.conf import settings
from IPython import embed

from django.forms.utils import ErrorList
from django.utils.html import format_html_join

import shortuuid

def unique_file_path(instance, filename):
    """
    Generate a random file name, but keep file extension and subdirectory.
    """
    if '/' in filename: # Extract subdirectory.
        subdir = filename.rsplit('/', 1)[0] # Split once, searching from end of string.
    else:
        subdir = ''
    extension = filename.split('.')[-1] # Extract file extension.
    new_filename = '{}.{}'.format(uuid.uuid4(), extension) # Generate random filename.
    file_path = os.path.join(settings.MEDIA_ROOT, subdir, new_filename)

    return file_path

def generate_share_id():
    """
    Creates a unique id for sharing experiments.
    """
    uuid = shortuuid.uuid() # Generates 22 digit uuid.
    short_uuid = uuid[:5] # Truncate to reasonable length.
    return short_uuid

class MyErrorList(ErrorList):
    """
    Modified version of the original Django ErrorList class
    (https://github.com/django/django/blob/master/django/forms/utils.py#L80).

    ErrorList.as_text() does not print asterisks anymore.
    """
    def as_text(self):
        return '\n'.join(self)
    
    def as_html_text(self):
        #return '<br />'.join(self)
        return format_html_join('','{}<br />', ((error,) for error in self))