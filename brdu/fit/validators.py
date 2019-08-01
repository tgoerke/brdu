import magic
from django.core.exceptions import ValidationError

from .utils import unique_file_path
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from django.utils.html import format_html, mark_safe

# Debugging
from IPython import embed

# CSV files
import pandas as pd

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
    upload.file.seek(0)
    file_type = magic.from_buffer(upload.file.read(1024), mime=True)
    #default_storage.delete(tmp_path)

    # Raise ValidationError if file type is wrong
    if file_type not in allowed_types:
        message = format_html('File type <code>{}</code> not supported.', file_type)
        raise ValidationError(message)

def ValidateCsv(upload):
    upload.file.seek(0) # Jump from EOF to first line again.
    headers = ['measurement_time', 'number_of_labeled_cells', 'number_of_all_cells']
    dtypes = {'measurement_time': 'float', 'number_of_labeled_cells': 'int', 'number_of_all_cells': 'int'}

    default_message = mark_safe('<strong>Invalid data found.</strong> Please check your CSV file.')
    try:
        df = pd.read_csv(upload.file, header=None, names=headers, dtype=dtypes, index_col=False)
        """
        header=None         : Don't use any rows as the column names.
        name=headers        : Use header names provided by this Django app.
        dtype=dtypes        : Data types for columns.
        index_col=False     : Too many cols won't be regarded as index_cols, but will raise an IndexError.

        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
        """
    except ValueError as error:
        # Indentify specific ValueError; Exception hierarchy: https://docs.python.org/3/library/exceptions.html#exception-hierarchy
        
        #if type(error) == type(UnicodeDecodeError): # https://stackoverflow.com/a/15844248/7192373
        #    raise ValidationError(default_message)

        # ValueError: cannot safely convert passed user dtype of int64 for float64 dtyped data in column 1
        if any('cannot safely convert passed user dtype of int64 for float64 dtyped data' in str(s) for s in error.args): # str() avoids TypeErrors, for instance when error subclass UnicodeDecodeError with bytes data in error.args occurs; https://stackoverflow.com/a/4843172/7192373
            invalid_column = int(error.args[0].split('column ')[-1]) # Get column number in error message.
            message = format_html('Please ensure your CSV file contains only <strong>whole numbers</strong> in <strong>column {}</strong>.', invalid_column+1)
            raise ValidationError(message)
    
        # ValueError: invalid literal for int() with base 10: 'b'
        elif any('invalid literal' in str(s) for s in error.args):
            message = mark_safe('Please ensure your CSV file contains <strong>only numbers</strong> and no literals.')
            raise ValidationError(message)

        # Unknown ValueError
        else:
            message = format_html('Unexpected ValueError: {}', type(error))
            raise ValidationError(message)
    
    except IndexError:
        # Too many columns in CSV file.
        message = mark_safe('Please ensure your CSV file has not more than <strong>3 columns.</strong>')
        raise ValidationError(message)

    except Exception as error:
        # All other errors
        message = format_html('Unexpected error: {}', type(error))

    pass