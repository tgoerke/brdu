import uuid
import os
from django.conf import settings
from IPython import embed

from django.forms.utils import ErrorList
from django.utils.html import format_html_join

def unique_file_path(instance, filename, subdir=''):
    """
    Generate a random file name, but keep file extension.
    """
    extension = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), extension) # random filename
    file_path = os.path.join(settings.MEDIA_ROOT, subdir, filename)

    return file_path

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