#!/bin/bash

# ===================================
# Script d'Installation Automatique
# Digital Signage - Serveur Personnel
# ===================================

set -e  # Arrêter en cas d'erreur

echo "╔════════════════════════════════════════════╗"
echo "║  Installation Digital Signage Server       ║"
echo "║  Version 1.0                               ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Vérifier si on est root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté en tant que root (sudo)"
    exit 1
fi

# Variables
PROJECT_DIR="/opt/digital_signage"
VENV_DIR="$PROJECT_DIR/venv"
DB_NAME="digital_signage"
DB_USER="signage_user"
NGINX_CONF="/etc/nginx/sites-available/digital_signage"

echo "📋 Configuration:"
echo "   Répertoire: $PROJECT_DIR"
echo "   Base de données: $DB_NAME"
echo ""

# Demander les informations
read -p "Nom de domaine (ou IP publique): " DOMAIN
read -sp "Mot de passe PostgreSQL: " DB_PASSWORD
echo ""
read -p "Utilisateur système (non-root): " SYSTEM_USER

# Valider l'utilisateur
if ! id "$SYSTEM_USER" &>/dev/null; then
    echo "❌ L'utilisateur $SYSTEM_USER n'existe pas"
    exit 1
fi

echo ""
echo "🚀 Démarrage de l'installation..."
echo ""

# ===================================
# 1. Mise à jour du système
# ===================================
echo "📦 Étape 1/10: Mise à jour du système..."
apt update && apt upgrade -y

# ===================================
# 2. Installation des dépendances
# ===================================
echo "📦 Étape 2/10: Installation des dépendances..."
apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    nginx \
    git curl build-essential libpq-dev \
    certbot python3-certbot-nginx

# ===================================
# 3. Configuration PostgreSQL
# ===================================
echo "🗄️  Étape 3/10: Configuration de PostgreSQL..."

# Créer la base de données et l'utilisateur
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'Africa/Abidjan';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "✅ Base de données créée"

# ===================================
# 4. Création du répertoire projet
# ===================================
echo "📁 Étape 4/10: Création du répertoire projet..."

mkdir -p $PROJECT_DIR
chown -R $SYSTEM_USER:$SYSTEM_USER $PROJECT_DIR

# ===================================
# 5. Environnement Python
# ===================================
echo "🐍 Étape 5/10: Configuration de l'environnement Python..."

sudo -u $SYSTEM_USER bash <<EOF
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
EOF

echo "✅ Environnement virtuel créé"

# ===================================
# 6. Fichier .env
# ===================================
echo "⚙️  Étape 6/10: Création du fichier .env..."

# Générer une SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

sudo -u $SYSTEM_USER cat > $PROJECT_DIR/.env <<EOF
# Configuration générée automatiquement
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Base de données
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
EOF

chown $SYSTEM_USER:$SYSTEM_USER $PROJECT_DIR/.env
chmod 600 $PROJECT_DIR/.env

echo "✅ Fichier .env créé"

# ===================================
# 7. Configuration Gunicorn
# ===================================
echo "🦄 Étape 7/10: Configuration de Gunicorn..."

# Socket Gunicorn
cat > /etc/systemd/system/gunicorn.socket <<EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

# Service Gunicorn
cat > /etc/systemd/system/gunicorn.service <<EOF
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$SYSTEM_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn.sock \\
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gunicorn.socket

echo "✅ Gunicorn configuré"

# ===================================
# 8. Configuration Nginx
# ===================================
echo "🌐 Étape 8/10: Configuration de Nginx..."

cat > $NGINX_CONF <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 100M;

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOF

# Activer le site
ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t

systemctl restart nginx
systemctl enable nginx

echo "✅ Nginx configuré"

# ===================================
# 9. Firewall
# ===================================
echo "🔒 Étape 9/10: Configuration du firewall..."

ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

echo "✅ Firewall configuré"

# ===================================
# 10. Créer les dossiers nécessaires
# ===================================
echo "📂 Étape 10/10: Création des dossiers..."

sudo -u $SYSTEM_USER mkdir -p $PROJECT_DIR/media
sudo -u $SYSTEM_USER mkdir -p $PROJECT_DIR/staticfiles
sudo -u $SYSTEM_USER mkdir -p /opt/backups

echo "✅ Dossiers créés"

# ===================================
# Résumé
# ===================================
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  ✅ Installation Terminée!                 ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📋 Prochaines étapes:"
echo ""
echo "1. Transférer votre code dans: $PROJECT_DIR"
echo "   Exemple avec SCP depuis votre PC:"
echo "   scp -r backend/* $SYSTEM_USER@$DOMAIN:$PROJECT_DIR/"
echo ""
echo "2. Installer les dépendances Python:"
echo "   sudo -u $SYSTEM_USER bash -c 'cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt'"
echo ""
echo "3. Exécuter les migrations:"
echo "   sudo -u $SYSTEM_USER bash -c 'cd $PROJECT_DIR && source venv/bin/activate && python manage.py migrate'"
echo ""
echo "4. Créer un superuser:"
echo "   sudo -u $SYSTEM_USER bash -c 'cd $PROJECT_DIR && source venv/bin/activate && python manage.py createsuperuser'"
echo ""
echo "5. Collecter les fichiers statiques:"
echo "   sudo -u $SYSTEM_USER bash -c 'cd $PROJECT_DIR && source venv/bin/activate && python manage.py collectstatic --noinput'"
echo ""
echo "6. Démarrer Gunicorn:"
echo "   systemctl start gunicorn.socket"
echo ""
echo "7. (Optionnel) Installer SSL avec Let's Encrypt:"
echo "   certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "🌐 Votre serveur sera accessible à:"
echo "   http://$DOMAIN"
echo ""
echo "📝 Fichier .env créé avec:"
echo "   - SECRET_KEY: Généré automatiquement"
echo "   - DB_PASSWORD: $DB_PASSWORD"
echo ""
echo "⚠️  IMPORTANT: Gardez ces informations en sécurité!"
