@echo off
mkdir ..\venv 2>nul
python3.7 -m venv ..\venv
..\venv\Scripts\pip.exe install -r ..\requirements.txt
..\venv\Scripts\python.exe -c "import reapy; reapy.configure_reaper()"
cmd /k
