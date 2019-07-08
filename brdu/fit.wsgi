"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

path = os.path.dirname(os.path.realpath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "brdu.settings"

# import django.core.handlers.wsgi
# application = django.core.handlers.wsgi.WSGIHandler()


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

os.chdir(path)

