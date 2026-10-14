@echo off
title Maak VR-viewer starter.exe
cd /d "%~dp0"
echo.
echo  Dit maakt een los programma (.exe) dat je kunt delen met
echo  medestudenten. Zij hebben dan geen Python nodig.
echo  Dit duurt 1 a 2 minuten.
echo.
pause

python -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo.
  echo  Installeren van PyInstaller lukte niet. Controleer je internetverbinding.
  pause
  exit /b
)

python -m PyInstaller --onefile --windowed --name "VR-viewer starter" --icon "%~dp0app.ico" --distpath "." --workpath "build" --specpath "build" vr_starter.pyw
if errorlevel 1 (
  echo.
  echo  Er ging iets mis bij het maken van de .exe.
  pause
  exit /b
)

rmdir /s /q build 2>nul
echo.
echo  Klaar! "VR-viewer starter.exe" staat nu in deze map.
echo.
pause
