[![Python 3.6](https://img.shields.io/badge/python-3.6-yellow.svg)](https://www.python.org/downloads/release/python-360/)
![Django 3.0](https://img.shields.io/badge/Django-3.0-green.svg)
[![license](https://img.shields.io/github/license/DAVFoundation/captain-n3m0.svg?style=flat-square)]()
# Open Classroom
This is an attempt to clone the best features of google classroom and educative.io using django.

## Screenshots 


<img src="screenshoot/dashboard_siswa.png" width="400"/><img src="screenshoot/forum.png" width="400"/> 
<img src="screenshoot/detailtugas.png" width="400"/> <img src="screenshoot/login.png" width="400"/> 
<img src="screenshoot/profil.png" width="400"/> <img src="screenshoot/Tambahtugas.png" width="400"/> 
<img src="screenshoot/userregister.PNG" width="400"/> <img src="screenshoot/detailtugas_siswa/png" width="400"/>
<img src="screenshoot/registrasi.png" width="400"/> <img src="screenshoot/liveboard.PNG" width="400"/> 


## Features Included 
- Custom Admin dashboard
- Create Classroom
- Join Classroom
- Add Posts 
- Create Assignments 
- Grade Assignments 
- Add Resources 
- WhiteBoard 
- Colaborative Whiteboard
- Courses 
- News Letter 
- Responsive, mobile-friendly design
- Forgot password 
- User registration
- Much more...

## Installation

**1. Clone Repository & Install Packages**
```sh
git clone https://github.com/mohamad1213/CLProject
pip install -r requirements.txt
```
**2. Setup Environment**
```sh
python -m  venv venv
source venv/bin/activate
``````
OR on Windows
```sh
python -m  venv venv
activate.bat
``````

**3. Migrate & Start Server**
```sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
