"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import logging.config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nd6bhj6v)wm1pvh-0mregnkfbx4#*6yu^!+8#^nnfcsu7@&0d*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '172.22.1.177', 'imc.zih.tu-dresden.de']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'crispy_forms',
    'widget_tweaks',

    # My apps
    'fit',

    'django_cleanup', # Should go after your apps; Automatically deletes old file for FileField and ImageField. It also deletes files on models instance deletion.

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'brdu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # https://docs.djangoproject.com/en/2.2/ref/settings/#media-root
            ],
        },
    },
]

WSGI_APPLICATION = 'brdu.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# List of static assets that aren’t tied to a particular app (i. e. the static/ directories inside the apps)

#STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, "static"),
#    '/var/www/static/',
#]

# Run "python manage.py collectstatic" to copy all files from the static folders into the STATIC_ROOT directory
# https://docs.djangoproject.com/en/2.1/howto/static-files/#deployment

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# https://blog.vivekshukla.xyz/uploading-file-using-api-django-rest-framework/

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

#USE_X_FORWARDED_HOST = True
#FORCE_SCRIPT_NAME = "/cellcycle"

# Logging configuration
# https://docs.djangoproject.com/en/2.2/topics/logging/#examples

# Disable Django's logging setup
#LOGGING_CONFIG = None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s.%(msecs)03d;%(levelname)s;%(name)s.%(funcName)s;%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    # Handler for logging to console
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
         # App logger
        'fit': {
            'handlers': ['console'],
            'level': 'DEBUG',
            #'propagate': True,
        },
        # Django framework code logger
        #'django': {
        #    'handlers': ['console'],
        #    'level': 'ERROR',
            #'propagate': True,
        #},
        # Catchall Root logger
        #'': {
        #    'handlers': ['console'],
        #    'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        #},
        # Prevent noisy modules from logging
        #'noisy_module': {
        #    'level': 'ERROR',
        #    'handlers': ['console'],
        #    'propagate': False,
        #},
    },
}
logging.config.dictConfig(LOGGING)

# The maximum number of parameters that may be received via GET or POST before a SuspiciousOperation (TooManyFields) is raised.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 4000 # https://docs.djangoproject.com/en/2.2/ref/settings/#data-upload-max-number-fields