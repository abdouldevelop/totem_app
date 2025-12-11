@echo off
echo ==========================================
echo Configuration du Pare-feu pour Digital Signage
echo ==========================================
echo.
echo Ajout de la regle de pare-feu...
echo.

REM Supprimer l'ancienne règle si elle existe
netsh advfirewall firewall delete rule name="Django Digital Signage (Port 8000)" >nul 2>&1

REM Ajouter la nouvelle règle
netsh advfirewall firewall add rule name="Django Digital Signage (Port 8000)" dir=in action=allow protocol=TCP localport=8000

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo SUCCES !
    echo ==========================================
    echo.
    echo La regle de pare-feu a ete ajoutee.
    echo Le serveur Django peut maintenant accepter
    echo les connexions depuis votre tablette.
    echo.
    echo Vous pouvez maintenant redemarrer l'application
    echo sur votre tablette.
    echo.
) else (
    echo.
    echo ==========================================
    echo ERREUR !
    echo ==========================================
    echo.
    echo Ce script doit etre execute en tant qu'ADMINISTRATEUR.
    echo.
    echo Comment faire:
    echo 1. Clic droit sur ce fichier
    echo 2. Choisir "Executer en tant qu'administrateur"
    echo.
)

echo.
pause
