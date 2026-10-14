@echo off
title VR-viewer starter
cd /d "%~dp0"

where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw "vr_starter.pyw"
  exit /b
)
where pyw >nul 2>nul
if %errorlevel%==0 (
  start "" pyw "vr_starter.pyw"
  exit /b
)

echo.
echo  Python is niet gevonden op deze computer.
echo.
echo  1. Ga naar https://www.python.org/downloads
echo  2. Installeer Python en vink "Add python.exe to PATH" aan
echo  3. Dubbelklik daarna opnieuw op dit bestand
echo.
start "" https://www.python.org/downloads/
pause
