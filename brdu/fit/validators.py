# http://blog.hayleyanderson.us/2015/07/18/validating-file-types-in-django/

import magic
from IPython import embed
from django.core.exceptions import ValidationError

from django.utils.safestring import mark_safe

CSV_TYPES = [
    'text/plain',
]

def ValidateFileType(upload, allowed_types=CSV_TYPES):
    """
    Checks file header with the libmagic file type identification library and
    returns HTML message if it does not match any allowed MIME type.
    """
    # Get MIME type of file using python-magic
    file_type = magic.from_file(upload.file.name, mime=True)

    # Return validation result
    if file_type not in allowed_types:
        message = mark_safe('File type (<code>{:s}</code>) not supported.'.format(file_type))
        #raise ValidationError(message)
        return message
    else:
        return None