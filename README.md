# BrdU cell cycle tool

Calculate cell cycle parameters from continuous labeling assays

Load environment with
```
. envs && pipenv shell
```

Then run backend server
```
cd backend
python manage.py runserver 0:8000
```

Or in one line
```
(cd backend && pipenv run python manage.py runserver 0:8000)
```

## Installation
Install requirement:

```
pipenv install --ignore-pipfile
```

Test run of fit code
```
python3 fit.py -i backend/fit/test.csv -o 123
```

Install Django web framework
```
pip install django django-rest-framework
```
## Python 3.4

To use older python 3.4 change the version string in the Pipfile
and initialize pipenv with
```
. envs && pipenv --python /usr/bin/python3.4 shell
```
