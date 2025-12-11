@echo off
echo =========================================
echo Digital Signage - Demarrage rapide
echo =========================================
echo.

REM Verifier si on est dans le bon dossier
if not exist "manage.py" (
    echo Erreur: Ce script doit etre execute depuis le dossier backend/
    pause
    exit /b 1
)

REM Creer l'environnement virtuel s'il n'existe pas
if not exist "venv" (
    echo Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dependances
echo Installation des dependances...
pip install -r requirements.txt

REM Creer le fichier .env s'il n'existe pas
if not exist ".env" (
    echo Creation du fichier .env...
    copy .env.example .env
    echo N'oubliez pas de modifier le fichier .env avec vos parametres!
)

REM Appliquer les migrations
echo Application des migrations...
python manage.py makemigrations
python manage.py migrate

REM Collecter les fichiers statiques
echo Collecte des fichiers statiques...
python manage.py collectstatic --noinput

REM Proposer de creer un superutilisateur
echo.
set /p create_user="Voulez-vous creer un superutilisateur? (o/n) "
if /i "%create_user%"=="o" (
    python manage.py createsuperuser
)

echo.
echo =========================================
echo Installation terminee!
echo =========================================
echo.
echo Pour demarrer le serveur:
echo   python manage.py runserver 0.0.0.0:8000
echo.
echo Acces admin: http://localhost:8000/admin
echo.
pause
