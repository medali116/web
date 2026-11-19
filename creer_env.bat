@echo off
cd /d "%~dp0"
set LOG=setup_log.txt
echo === Creation de l'environnement virtuel "env" (Python 3.12) === > %LOG%
where uv >> %LOG% 2>&1
if errorlevel 1 goto avec_py

:avec_uv
uv venv env --python 3.12 --no-project >> %LOG% 2>&1
uv pip install --python env\Scripts\python.exe -r requirements.txt >> %LOG% 2>&1
goto verif

:avec_py
py -3.12 -m venv env >> %LOG% 2>&1
env\Scripts\python.exe -m pip install -r requirements.txt >> %LOG% 2>&1

:verif
echo === Versions === >> %LOG%
env\Scripts\python.exe --version >> %LOG% 2>&1
env\Scripts\python.exe -m django --version >> %LOG% 2>&1
echo === Migrations === >> %LOG%
cd GestionCabinetMedical
..\env\Scripts\python.exe manage.py makemigrations AccountApp AppointmentApp >> ..\%LOG% 2>&1
..\env\Scripts\python.exe manage.py migrate >> ..\%LOG% 2>&1
cd ..
echo FIN >> %LOG%
type %LOG%
pause
