@echo off
setlocal
cd /d "%~dp0"
echo KADOMA - Windows x64 native build
echo Requires 64-bit Python 3.11-3.13 and internet access to download build dependencies.
py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements-desktop.txt -r requirements-dev.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 goto fail
.venv\Scripts\python.exe scripts\build.py --mode both
if errorlevel 1 goto fail
echo.
echo Builds are in the release folder:
echo   KADOMA-*-Windows-x64-standalone.exe   one file, copy it anywhere
echo   KADOMA-*-Windows-x64-portable.zip     folder build, faster start
echo Inno Setup 6 is required for Setup.exe; without it the two builds above are used.
pause
exit /b 0
:fail
echo.
echo Build failed. Read the message above. No compatible installer is claimed to exist.
pause
exit /b 1
