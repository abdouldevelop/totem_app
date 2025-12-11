@echo off
echo =========================================
echo DIAGNOSTIC DIGITAL SIGNAGE
echo =========================================
echo.

REM Verifier si on est dans le bon dossier
if not exist "manage.py" (
    echo Erreur: Ce script doit etre execute depuis le dossier backend/
    pause
    exit /b 1
)

REM Activer l'environnement virtuel s'il existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Lancer le diagnostic
python check_setup.py

echo.
pause
