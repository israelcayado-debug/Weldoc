@echo off
setlocal

cd /d %~dp0
python manage.py spectacular --file ..\openapi.yaml --settings=config.settings.dev
