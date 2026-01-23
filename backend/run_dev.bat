@echo off
setlocal

set DJANGO_SETTINGS_MODULE=config.settings.dev
cd /d %~dp0

set PORT=%1
if "%PORT%"=="" set PORT=8000

python manage.py runserver 127.0.0.1:%PORT% --settings=config.settings.dev
