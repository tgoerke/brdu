import magic
from django.core.exceptions import ValidationError

from .utils import unique_file_path
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from django.utils.html import format_html

from IPython import embed

CSV_TYPES = [
    'text/plain',
]

def ValidateFileType(upload, allowed_types=CSV_TYPES):
    """
    Checks file header with the libmagic file type identification library and
    returns HTML message if it does not match any allowed MIME type.

    http://blog.hayleyanderson.us/2015/07/18/validating-file-types-in-django/
    """
    # Get MIME type of file using python-magic
    #tmp_path = unique_file_path(instance=None, filename=upload.file.name)
    #default_storage.save(tmp_path, ContentFile(upload.file.read()))
    file_type = magic.from_buffer(upload.file.read(1024), mime=True)
    #default_storage.delete(tmp_path)

    # Raise ValidationError if file type is wrong
    if file_type not in allowed_types:
        message = format_html('File type <code>{}</code> not supported.', file_type)
        raise ValidationError(message)