#!/bin/bash

# ===================================
# Script de Vérification Pré-Déploiement
# Digital Signage Backend
# ===================================

set -e

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Compteurs
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Vérification Pré-Déploiement             ║${NC}"
echo -e "${BLUE}║  Digital Signage Backend                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Fonctions d'affichage
check_ok() {
    echo -e "  ${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "  ${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

check_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    ((CHECKS_WARNING++))
}

section_header() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

# ===================================
# 1. Vérification de l'environnement
# ===================================
section_header "1. Environnement Local"

# Vérifier que nous sommes dans le bon répertoire
if [ -f "manage.py" ] && [ -f "requirements.txt" ]; then
    check_ok "Répertoire backend détecté"
else
    check_fail "Fichiers Django non trouvés. Exécutez ce script depuis le dossier backend/"
    exit 1
fi

# Vérifier Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    check_ok "Python installé (version $PYTHON_VERSION)"
else
    check_fail "Python 3 n'est pas installé"
fi

# Vérifier pip
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    check_ok "pip installé"
else
    check_fail "pip n'est pas installé"
fi

# ===================================
# 2. Vérification des fichiers de configuration
# ===================================
section_header "2. Fichiers de Configuration"

# Fichiers requis
REQUIRED_FILES=(
    "requirements.txt"
    ".env.example"
    ".env.production"
    "deploy.sh"
    "install_server.sh"
    "gunicorn.service.example"
    "nginx.conf.example"
    "DEPLOYMENT_GUIDE.md"
    "PRE_DEPLOYMENT_CHECKLIST.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_ok "Fichier trouvé: $file"
    else
        check_fail "Fichier manquant: $file"
    fi
done

# Vérifier les scripts sont exécutables
if [ -x "deploy.sh" ]; then
    check_ok "deploy.sh est exécutable"
else
    check_warning "deploy.sh n'est pas exécutable (chmod +x deploy.sh)"
fi

if [ -x "install_server.sh" ]; then
    check_ok "install_server.sh est exécutable"
else
    check_warning "install_server.sh n'est pas exécutable (chmod +x install_server.sh)"
fi

# ===================================
# 3. Vérification de la configuration Django
# ===================================
section_header "3. Configuration Django"

# Vérifier config/settings.py
if [ -f "config/settings.py" ]; then
    check_ok "settings.py trouvé"

    # Vérifier les imports importants
    if grep -q "python-decouple" requirements.txt; then
        check_ok "python-decouple dans requirements.txt"
    else
        check_fail "python-decouple manquant dans requirements.txt"
    fi

    if grep -q "gunicorn" requirements.txt; then
        check_ok "gunicorn dans requirements.txt"
    else
        check_fail "gunicorn manquant dans requirements.txt"
    fi

    if grep -q "psycopg2" requirements.txt; then
        check_ok "psycopg2 dans requirements.txt"
    else
        check_warning "psycopg2 manquant (PostgreSQL ne sera pas supporté)"
    fi
else
    check_fail "config/settings.py non trouvé"
fi

# Vérifier config/wsgi.py
if [ -f "config/wsgi.py" ]; then
    check_ok "wsgi.py trouvé"
else
    check_fail "config/wsgi.py non trouvé"
fi

# ===================================
# 4. Vérification du fichier .env
# ===================================
section_header "4. Configuration Environnement"

if [ -f ".env" ]; then
    check_warning ".env existe (assurez-vous qu'il n'est pas committé sur Git)"

    # Vérifier DEBUG
    if grep -q "DEBUG=False" .env; then
        check_ok "DEBUG=False dans .env"
    elif grep -q "DEBUG=True" .env; then
        check_fail "DEBUG=True dans .env (doit être False en production!)"
    else
        check_warning "DEBUG non défini dans .env"
    fi

    # Vérifier SECRET_KEY
    if grep -q "SECRET_KEY=" .env; then
        SECRET_KEY=$(grep "SECRET_KEY=" .env | cut -d'=' -f2)
        if [ ${#SECRET_KEY} -gt 40 ]; then
            check_ok "SECRET_KEY définie (longueur: ${#SECRET_KEY})"
        else
            check_warning "SECRET_KEY semble trop courte"
        fi
    else
        check_fail "SECRET_KEY non définie dans .env"
    fi

    # Vérifier ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS=" .env; then
        check_ok "ALLOWED_HOSTS défini"
    else
        check_warning "ALLOWED_HOSTS non défini"
    fi
else
    check_ok ".env n'existe pas (sera créé sur le serveur)"
fi

# Vérifier .env.production
if [ -f ".env.production" ]; then
    check_ok ".env.production existe"

    # Vérifier qu'il contient des placeholders
    if grep -q "CHANGEZ_CECI" .env.production || grep -q "votre-domaine" .env.production; then
        check_ok ".env.production contient des placeholders (à remplacer sur le serveur)"
    else
        check_warning ".env.production semble déjà configuré"
    fi
else
    check_fail ".env.production manquant"
fi

# ===================================
# 5. Vérification Git
# ===================================
section_header "5. Contrôle de Version"

if [ -d ".git" ]; then
    check_ok "Dépôt Git initialisé"

    # Vérifier .gitignore
    if [ -f ".gitignore" ]; then
        check_ok ".gitignore trouvé"

        # Vérifier que .env est ignoré
        if grep -q "^\.env$" .gitignore || grep -q "^\.env" .gitignore; then
            check_ok ".env est dans .gitignore"
        else
            check_fail ".env n'est PAS dans .gitignore (risque de sécurité!)"
        fi

        # Vérifier que .venv est ignoré
        if grep -q "venv" .gitignore || grep -q "\.venv" .gitignore; then
            check_ok "environnement virtuel ignoré"
        else
            check_warning "venv/virtualenv devrait être dans .gitignore"
        fi
    else
        check_warning ".gitignore non trouvé"
    fi

    # Vérifier les modifications non committées
    if git diff --quiet && git diff --cached --quiet; then
        check_ok "Pas de modifications non committées"
    else
        check_warning "Il y a des modifications non committées"
    fi
else
    check_warning "Git n'est pas initialisé (recommandé pour le déploiement)"
fi

# ===================================
# 6. Vérification des applications Django
# ===================================
section_header "6. Applications Django"

if [ -d "apps" ]; then
    check_ok "Dossier apps/ trouvé"

    # Compter les apps
    APP_COUNT=$(find apps -maxdepth 1 -type d | wc -l)
    check_ok "$APP_COUNT applications Django trouvées"
else
    check_warning "Dossier apps/ non trouvé"
fi

# ===================================
# 7. Vérification de la structure
# ===================================
section_header "7. Structure du Projet"

EXPECTED_DIRS=("config" "media" "templates")

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_ok "Dossier $dir/ trouvé"
    else
        check_warning "Dossier $dir/ non trouvé"
    fi
done

# ===================================
# 8. Suggestions de sécurité
# ===================================
section_header "8. Sécurité"

# Vérifier les mots de passe par défaut dans les fichiers
if grep -r "password.*=.*password" . --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" 2>/dev/null | grep -v ".pyc" > /dev/null; then
    check_warning "Mots de passe par défaut trouvés dans le code"
fi

# Vérifier les TODO
if grep -r "TODO\|FIXME" . --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" 2>/dev/null | grep -v ".pyc" > /dev/null; then
    check_warning "TODO/FIXME trouvés dans le code"
fi

# ===================================
# 9. Documentation
# ===================================
section_header "9. Documentation"

DOC_FILES=("DEPLOYMENT_GUIDE.md" "PRE_DEPLOYMENT_CHECKLIST.md" "DEPLOYMENT_README.md")

for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        check_ok "$doc disponible"
    else
        check_warning "$doc manquant"
    fi
done

# ===================================
# Résumé
# ===================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Résumé de la Vérification                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}✓${NC} Vérifications réussies: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "  ${YELLOW}⚠${NC} Avertissements:        ${YELLOW}$CHECKS_WARNING${NC}"
echo -e "  ${RED}✗${NC} Vérifications échouées: ${RED}$CHECKS_FAILED${NC}"
echo ""

# Conclusion
if [ $CHECKS_FAILED -eq 0 ] && [ $CHECKS_WARNING -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Excellent! Le projet est prêt pour le déploiement.${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
elif [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠ Le projet est presque prêt. Vérifiez les avertissements.${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ Des problèmes ont été détectés. Corrigez-les avant de déployer.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi

echo ""
echo "Prochaines étapes:"
echo "  1. Consultez DEPLOYMENT_README.md pour choisir votre méthode"
echo "  2. Consultez PRE_DEPLOYMENT_CHECKLIST.md pour la checklist complète"
echo "  3. Suivez DEPLOYMENT_GUIDE.md pour les instructions détaillées"
echo ""

# Code de sortie
if [ $CHECKS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
