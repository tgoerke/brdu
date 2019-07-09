import uuid
import os
from django.conf import settings

def unique_file_path(instance, filename, subdir = 'csv/'):
    """
    Generate a random file name with .csv extension.
    """
    extension = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), extension) # random filename
    file_path = os.path.join(settings.MEDIA_ROOT, subdir, filename)
    
    return file_path