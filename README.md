# BrdU cell cycle tool

Calculate cell cycle parameters from continuous labeling assays.

## Installation

Use one virtual environment of your choice. Exemplary installation using ```venv``` or ```pipenv``` is described below.

### Install dependencies

#### venv

	$ python3 -m venv venv
	$ source venv/bin/activate

    $ pip install -r requirements.txt

#### pipenv

Install requirements:

    $ pipenv install --ignore-pipfile

Test run of fit code

    $ python3 fit.py -i brdu/fit/test.csv -o 123

Install Django web framework

    $ pip install django django-rest-framework

#### Python 3.4

To use older python 3.4 change the version string in the Pipfile
and initialize pipenv with

    $ . envs && pipenv --python /usr/bin/python3.4 shell

### Database

If you are going to start the server for the first time or if the Django models have changed, you need to generate the database file first.

    $ cd brdu
    $ python manage.py makemigrations
    $ python manage.py migrate --run-syncdb

### Static files

Furthermore all static files need to be copied to ```STATIC_ROOT```.

    $ python manage.py collectstatic

## Running Django

### Load environment

#### venv

    $ source venv/bin/activate

#### pipenv

Load environment with

    $ . envs && pipenv shell

### Start server

Please make sure, that you have installed the [dependencies](#install-dependencies) and the [database](#database) as well as collected the [static files](#static-files).

Run the server:

    $ cd brdu
    $ python manage.py runserver

The Cell Cycle Analyzer can be found under: http://127.0.0.1:8000/

## Deployment

### Disable debug mode

Set [```DEBUG = False```](https://docs.djangoproject.com/en/2.2/ref/settings/#debug) in ```settings.py``` to disable the display of detailed traceback information, which could pose a security risk.

### Set ```ALLOWED_HOSTS```

[```ALLOWED_HOSTS```](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-ALLOWED_HOSTS) must be set in ```settings.py``` according to your server. Otherwise this will result in all requests being returned as *Bad Request (400)*.

### Set a new ```SECRET_KEY```

Change the [```SECRET_KEY```](https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key) in ```settings.py``` to a unique, unpredictable value. Do not carry the key from development (for instance from this GitHub repository) over to the deployment server!

Django creates an unique key automatically when a [new project is started](https://docs.djangoproject.com/en/2.2/ref/django-admin/#django-admin-startproject).

    $ django-admin startproject myproject

So you can also use this as a generator for your server key.

### Sessions

Expired sessions should be [purged regularly](https://docs.djangoproject.com/en/2.2/topics/http/sessions/#clearing-the-session-store) (for example as a daily cron job) with:

    $ python manage.py clearsessions
