# BrdU cell cycle tool

Calculate cell cycle parameters from continuous labeling assays

Load environment with
	. envs && pipenv shell

Then run backend server
	cd backend
	python manage.py runserver 0:8000
	
Open http://127.0.0.1:8000/

Backend Admin:
http://127.0.0.1:8000/admin


## Installation
Install requirements for brdu:

sudo apt-get install gcc python3-dev
pip install numpy scipy iminuit matplotlib

Test run:
python3 fit.py -i test.csv -o out/123

