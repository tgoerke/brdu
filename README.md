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
	
Open http://127.0.0.1:8000/

Backend Admin:
http://127.0.0.1:8000/admin


## Installation
Install requirements for brdu:

```
sudo apt-get install gcc python3-dev
pip install numpy scipy iminuit matplotlib
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
