@echo off
echo =========================================
echo Digital Signage - Demarrage du serveur
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
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
)

echo.
echo =========================================
echo Demarrage du serveur sur 0.0.0.0:8000
echo Accessible depuis le reseau local
echo =========================================
echo.
echo URL locale: http://localhost:8000
echo URL reseau: http://192.168.50.80:8000
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

REM Demarrer le serveur sur toutes les interfaces
python manage.py runserver 0.0.0.0:8000
