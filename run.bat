@echo off
cd Backend
call venv\Scripts\activate
python manage.py runserver
pause 