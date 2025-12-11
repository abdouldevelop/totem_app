@echo off
echo =========================================
echo Configuration du Pare-feu Windows
echo =========================================
echo.
echo Ce script va autoriser Python a accepter
echo les connexions sur le port 8000
echo.
echo ATTENTION: Necessite les droits administrateur
echo.
pause

REM Ajouter une regle de pare-feu pour autoriser le port 8000
netsh advfirewall firewall add rule name="Django Digital Signage (Port 8000)" dir=in action=allow protocol=TCP localport=8000

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================
    echo Regle de pare-feu ajoutee avec succes!
    echo =========================================
    echo.
    echo Le serveur Django peut maintenant accepter
    echo les connexions depuis le reseau local.
    echo.
) else (
    echo.
    echo =========================================
    echo ERREUR: Impossible d'ajouter la regle
    echo =========================================
    echo.
    echo Veuillez executer ce script en tant qu'administrateur:
    echo - Clic droit sur le fichier
    echo - "Executer en tant qu'administrateur"
    echo.
)

pause
