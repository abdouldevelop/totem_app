#!/bin/bash

# ===================================
# SCRIPT DE DÉPLOIEMENT PRODUCTION
# Digital Signage Backend
# ===================================

set -e  # Arrêter en cas d'erreur

echo "=================================="
echo "Déploiement Digital Signage Backend"
echo "=================================="

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "manage.py" ]; then
    log_error "Ce script doit être exécuté depuis le dossier backend/"
    exit 1
fi

# Vérifier que le fichier .env existe
if [ ! -f ".env" ]; then
    log_error "Le fichier .env n'existe pas!"
    log_warning "Copiez .env.production et configurez-le :"
    echo "  cp .env.production .env"
    echo "  nano .env  # Modifiez les valeurs"
    exit 1
fi

# Vérifier que DEBUG=False en production
if grep -q "DEBUG=True" .env; then
    log_error "DEBUG est activé dans .env ! Impossible de déployer en production."
    exit 1
fi

log_info "1. Activation de l'environnement virtuel..."
if [ -d "venv" ]; then
    source venv/bin/activate
else
    log_error "L'environnement virtuel n'existe pas. Créez-le avec : python3 -m venv venv"
    exit 1
fi

log_info "2. Installation des dépendances..."
pip install -r requirements.txt --quiet

log_info "3. Exécution des migrations de la base de données..."
python manage.py migrate --no-input

log_info "4. Collecte des fichiers statiques..."
python manage.py collectstatic --no-input --clear

log_info "5. Vérification de la configuration Django..."
python manage.py check --deploy

log_info "6. Création d'un superutilisateur (si nécessaire)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print("Création du superutilisateur 'admin'...")
    print("IMPORTANT : Changez le mot de passe après le déploiement !")
else:
    print("Le superutilisateur existe déjà.")
EOF

# Redémarrer Gunicorn si le service existe
if systemctl list-units --full -all | grep -q "gunicorn-digital-signage.service"; then
    log_info "7. Redémarrage de Gunicorn..."
    sudo systemctl restart gunicorn-digital-signage

    log_info "8. Vérification du statut de Gunicorn..."
    if systemctl is-active --quiet gunicorn-digital-signage; then
        log_info "✓ Gunicorn est en cours d'exécution"
    else
        log_error "✗ Gunicorn n'a pas démarré correctement"
        sudo systemctl status gunicorn-digital-signage
        exit 1
    fi
else
    log_warning "Le service Gunicorn n'est pas configuré. Démarrez-le manuellement."
fi

# Recharger Nginx si installé
if command -v nginx &> /dev/null; then
    log_info "9. Rechargement de Nginx..."
    sudo nginx -t && sudo systemctl reload nginx
else
    log_warning "Nginx n'est pas installé ou non configuré."
fi

echo ""
log_info "=================================="
log_info "✓ Déploiement terminé avec succès !"
log_info "=================================="
echo ""
log_info "Prochaines étapes :"
echo "  1. Testez l'API : curl https://votre-domaine.com/api/"
echo "  2. Accédez à l'admin : https://votre-domaine.com/admin/"
echo "  3. Vérifiez les logs : sudo journalctl -u gunicorn-digital-signage -f"
echo ""
