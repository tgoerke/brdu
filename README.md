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

### Sessions

Expired sessions should be [purged regularly](https://docs.djangoproject.com/en/2.2/topics/http/sessions/#clearing-the-session-store) (for example as a daily cron job) with:

    $ python manage.py clearsessions
