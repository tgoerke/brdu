"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

#import os

#from django.core.wsgi import get_wsgi_application

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

#application = get_wsgi_application()

#python_home = '/home/julian/.local/share/virtualenvs/brdu-B_Fak0wL'
#activate_this = python_home + '/bin/activate_this.py'

#exec(compile(open(activate_this,"rb").read(),activate_this, 'exec'), dict(__file__=activate_this))

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fit.settings")

application = get_wsgi_application()
