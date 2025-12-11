# Guide de Déploiement - Digital Signage

Ce guide vous accompagne dans le déploiement complet de votre système de digital signage sur un serveur de production.

## Table des matières

1. [Prérequis](#prérequis)
2. [Options de déploiement](#options-de-déploiement)
3. [Déploiement sur serveur Linux (Méthode recommandée)](#déploiement-sur-serveur-linux)
4. [Déploiement rapide sur Heroku](#déploiement-rapide-sur-heroku)
5. [Configuration après déploiement](#configuration-après-déploiement)
6. [Maintenance et surveillance](#maintenance-et-surveillance)
7. [Dépannage](#dépannage)

---

## Prérequis

### Serveur recommandé
- **OS**: Ubuntu 22.04 LTS ou Debian 11+
- **RAM**: Minimum 2 GB (4 GB recommandé)
- **CPU**: 2 cœurs minimum
- **Stockage**: 20 GB minimum (selon le volume de médias)
- **Accès**: SSH avec privilèges sudo

### Nom de domaine
- Un nom de domaine pointant vers votre serveur
- Ou l'adresse IP publique de votre serveur

### Base de données
Le projet supporte:
- PostgreSQL (recommandé pour la production)
- SQLite (développement uniquement)

---

## Options de déploiement

### Option 1: Installation automatique (Recommandé)
Utilisez le script `install_server.sh` pour une installation complète et automatisée.

### Option 2: Installation manuelle
Suivez le guide étape par étape ci-dessous.

### Option 3: Heroku
Pour un déploiement rapide sans gérer de serveur, consultez `HEROKU_QUICKSTART.md`.

---

## Déploiement sur serveur Linux

### Étape 1: Préparation du serveur

#### 1.1 Connexion au serveur
```bash
ssh votre-utilisateur@votre-serveur.com
```

#### 1.2 Installation automatique (RECOMMANDÉ)

Téléchargez et exécutez le script d'installation:

```bash
# Télécharger le script
wget https://votre-repo.com/install_server.sh
# ou
curl -O https://votre-repo.com/install_server.sh

# Rendre le script exécutable
chmod +x install_server.sh

# Exécuter en tant que root
sudo ./install_server.sh
```

Le script va:
- Installer toutes les dépendances système
- Configurer PostgreSQL
- Créer l'environnement Python
- Configurer Gunicorn et Nginx
- Configurer le firewall

**Suivez les instructions du script et notez les informations importantes!**

#### 1.3 Installation manuelle (Alternative)

Si vous préférez installer manuellement:

##### a) Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

##### b) Installation des dépendances
```bash
sudo apt install -y \
    python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    nginx \
    git curl build-essential libpq-dev \
    certbot python3-certbot-nginx
```

##### c) Configuration PostgreSQL
```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données et l'utilisateur
CREATE DATABASE digital_signage_prod;
CREATE USER signage_user WITH PASSWORD 'votre_mot_de_passe_securise';
ALTER ROLE signage_user SET client_encoding TO 'utf8';
ALTER ROLE signage_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE signage_user SET timezone TO 'Africa/Abidjan';
GRANT ALL PRIVILEGES ON DATABASE digital_signage_prod TO signage_user;
\q
```

##### d) Création du répertoire projet
```bash
# Créer le répertoire
sudo mkdir -p /opt/digital_signage
sudo chown -R $USER:$USER /opt/digital_signage
cd /opt/digital_signage
```

### Étape 2: Transfert des fichiers

#### Option A: Avec Git (Recommandé)
```bash
cd /opt/digital_signage
git clone https://votre-repo.com/digital_signage.git .
```

#### Option B: Avec SCP depuis votre machine locale
```bash
# Depuis votre machine locale (Windows/Linux/Mac)
cd C:\Programme\digital_signage_project\backend
scp -r * votre-utilisateur@votre-serveur.com:/opt/digital_signage/
```

#### Option C: Avec rsync (plus rapide pour les mises à jour)
```bash
# Depuis votre machine locale
rsync -avz --exclude='.venv' --exclude='*.pyc' --exclude='__pycache__' \
    C:\Programme\digital_signage_project\backend/ \
    votre-utilisateur@votre-serveur.com:/opt/digital_signage/
```

### Étape 3: Configuration de l'environnement

#### 3.1 Créer l'environnement virtuel Python
```bash
cd /opt/digital_signage
python3 -m venv venv
source venv/bin/activate
```

#### 3.2 Installer les dépendances Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.3 Créer et configurer le fichier .env
```bash
# Copier le modèle
cp .env.production .env

# Éditer le fichier
nano .env
```

Modifiez les valeurs suivantes dans `.env`:

```env
# Django Configuration
SECRET_KEY=VOTRE_CLE_SECRETE_GENEREE
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,VOTRE_IP

# Database Configuration
DB_NAME=digital_signage_prod
DB_USER=signage_user
DB_PASSWORD=votre_mot_de_passe_securise
DB_HOST=localhost
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://votre-domaine.com
```

**Générer une SECRET_KEY sécurisée:**
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### 3.4 Sécuriser le fichier .env
```bash
chmod 600 .env
chown $USER:$USER .env
```

### Étape 4: Configuration Django

#### 4.1 Exécuter les migrations
```bash
source venv/bin/activate
python manage.py migrate
```

#### 4.2 Créer un superutilisateur
```bash
python manage.py createsuperuser
```

#### 4.3 Collecter les fichiers statiques
```bash
python manage.py collectstatic --noinput
```

#### 4.4 Créer les dossiers nécessaires
```bash
mkdir -p media staticfiles
chmod 755 media staticfiles
```

### Étape 5: Configuration de Gunicorn

#### 5.1 Créer le fichier de service systemd
```bash
sudo nano /etc/systemd/system/gunicorn-digital-signage.service
```

Copiez le contenu de `gunicorn.service.example` et **remplacez les chemins**:

```ini
[Unit]
Description=Gunicorn daemon for Digital Signage
After=network.target

[Service]
Type=notify
User=votre-utilisateur
Group=www-data
WorkingDirectory=/opt/digital_signage
Environment="PATH=/opt/digital_signage/venv/bin"

ExecStart=/opt/digital_signage/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --access-logfile /var/log/gunicorn/digital-signage-access.log \
    --error-logfile /var/log/gunicorn/digital-signage-error.log \
    --log-level info \
    config.wsgi:application

Restart=always
RestartSec=10

PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

#### 5.2 Créer le dossier des logs
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown -R $USER:www-data /var/log/gunicorn
```

#### 5.3 Démarrer et activer Gunicorn
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn-digital-signage
sudo systemctl enable gunicorn-digital-signage
sudo systemctl status gunicorn-digital-signage
```

### Étape 6: Configuration de Nginx

#### 6.1 Créer la configuration Nginx
```bash
sudo nano /etc/nginx/sites-available/digital-signage
```

Copiez le contenu de `nginx.conf.example` et **remplacez**:
- `votre-domaine.com` par votre vrai domaine
- `/chemin/vers/digital_signage_project` par `/opt/digital_signage`

#### 6.2 Activer le site
```bash
sudo ln -s /etc/nginx/sites-available/digital-signage /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

#### 6.3 Tester et redémarrer Nginx
```bash
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Étape 7: Configuration SSL avec Let's Encrypt

#### 7.1 Installer Certbot (si non fait)
```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### 7.2 Obtenir un certificat SSL
```bash
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

Suivez les instructions et choisissez:
- Email pour les notifications importantes
- Accepter les conditions
- Redirection automatique HTTP vers HTTPS (recommandé)

#### 7.3 Renouvellement automatique
Certbot configure automatiquement le renouvellement. Testez-le:
```bash
sudo certbot renew --dry-run
```

### Étape 8: Configuration du Firewall

#### 8.1 Configurer UFW
```bash
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### Étape 9: Vérification finale

#### 9.1 Tester l'API
```bash
curl https://votre-domaine.com/api/
```

#### 9.2 Accéder à l'interface admin
Ouvrez dans votre navigateur:
```
https://votre-domaine.com/admin/
```

#### 9.3 Vérifier les logs
```bash
# Logs Gunicorn
sudo journalctl -u gunicorn-digital-signage -f

# Logs Nginx
sudo tail -f /var/log/nginx/digital-signage-error.log
```

---

## Déploiement rapide sur Heroku

Pour un déploiement rapide sans gérer de serveur, consultez le guide détaillé:

```bash
cat HEROKU_QUICKSTART.md
```

Ou suivez ces étapes rapides:

```bash
# 1. Installer Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Se connecter
heroku login

# 3. Créer l'application
heroku create nom-de-votre-app

# 4. Ajouter PostgreSQL
heroku addons:create heroku-postgresql:mini

# 5. Déployer
git push heroku main

# 6. Exécuter les migrations
heroku run python manage.py migrate

# 7. Créer un superutilisateur
heroku run python manage.py createsuperuser
```

---

## Configuration après déploiement

### 1. Configurer les sauvegardes automatiques

#### PostgreSQL
```bash
# Créer un script de sauvegarde
sudo nano /opt/backups/backup_db.sh
```

Contenu:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_NAME="digital_signage_prod"

mkdir -p $BACKUP_DIR

pg_dump $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Supprimer les sauvegardes de plus de 30 jours
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Sauvegarde terminée: backup_$DATE.sql.gz"
```

```bash
chmod +x /opt/backups/backup_db.sh

# Ajouter à cron (quotidien à 2h du matin)
sudo crontab -e
```

Ajouter:
```
0 2 * * * /opt/backups/backup_db.sh >> /var/log/backup.log 2>&1
```

### 2. Configurer la rotation des logs

```bash
sudo nano /etc/logrotate.d/digital-signage
```

Contenu:
```
/var/log/gunicorn/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload gunicorn-digital-signage > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/digital-signage-*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
```

### 3. Configurer la surveillance

#### Installer un outil de surveillance (optionnel)
```bash
# Exemple avec htop
sudo apt install htop

# Ou avec Glances (plus complet)
sudo apt install glances
```

---

## Maintenance et surveillance

### Commandes utiles

#### Gestion des services
```bash
# Redémarrer l'application
sudo systemctl restart gunicorn-digital-signage
sudo systemctl restart nginx

# Voir le statut
sudo systemctl status gunicorn-digital-signage
sudo systemctl status nginx

# Voir les logs en temps réel
sudo journalctl -u gunicorn-digital-signage -f
sudo tail -f /var/log/nginx/digital-signage-error.log
```

#### Gestion Django
```bash
cd /opt/digital_signage
source venv/bin/activate

# Vérifier la configuration
python manage.py check --deploy

# Créer des migrations
python manage.py makemigrations
python manage.py migrate

# Collecter les statiques
python manage.py collectstatic --noinput
```

### Mises à jour du code

#### Méthode avec Git
```bash
cd /opt/digital_signage
git pull origin main

# Activer l'environnement
source venv/bin/activate

# Installer les nouvelles dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Collecter les statiques
python manage.py collectstatic --noinput

# Redémarrer Gunicorn
sudo systemctl restart gunicorn-digital-signage
```

#### Méthode avec le script de déploiement
```bash
cd /opt/digital_signage
./deploy.sh
```

Le script `deploy.sh` effectue automatiquement:
- Installation des dépendances
- Migrations
- Collecte des statiques
- Vérification de la configuration
- Redémarrage des services

---

## Dépannage

### Problème: L'application ne démarre pas

#### 1. Vérifier les logs Gunicorn
```bash
sudo journalctl -u gunicorn-digital-signage -n 50
```

#### 2. Vérifier la configuration Django
```bash
cd /opt/digital_signage
source venv/bin/activate
python manage.py check
```

#### 3. Vérifier le fichier .env
```bash
cat .env
```
Assurez-vous que:
- `DEBUG=False`
- `SECRET_KEY` est défini
- Les informations de base de données sont correctes

### Problème: Erreur 502 Bad Gateway

#### 1. Vérifier que Gunicorn fonctionne
```bash
sudo systemctl status gunicorn-digital-signage
```

#### 2. Tester Gunicorn manuellement
```bash
cd /opt/digital_signage
source venv/bin/activate
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

#### 3. Vérifier la configuration Nginx
```bash
sudo nginx -t
sudo systemctl status nginx
```

### Problème: Les fichiers statiques ne se chargent pas

#### 1. Collecter les statiques
```bash
cd /opt/digital_signage
source venv/bin/activate
python manage.py collectstatic --noinput --clear
```

#### 2. Vérifier les permissions
```bash
ls -la /opt/digital_signage/staticfiles/
chmod -R 755 /opt/digital_signage/staticfiles/
```

#### 3. Vérifier la configuration Nginx
```bash
sudo nano /etc/nginx/sites-available/digital-signage
```
Assurez-vous que le chemin `/static/` pointe vers le bon répertoire.

### Problème: Erreur de connexion à la base de données

#### 1. Vérifier que PostgreSQL fonctionne
```bash
sudo systemctl status postgresql
```

#### 2. Tester la connexion
```bash
psql -U signage_user -d digital_signage_prod -h localhost
```

#### 3. Vérifier le fichier .env
Assurez-vous que:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` sont corrects
- `DB_HOST=localhost`
- `DB_PORT=5432`

### Problème: Erreur CORS

Si les écrans ne peuvent pas se connecter à l'API:

#### 1. Vérifier la configuration CORS dans .env
```bash
nano .env
```

Ajoutez toutes les origines autorisées:
```env
CORS_ALLOWED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
```

#### 2. Redémarrer Gunicorn
```bash
sudo systemctl restart gunicorn-digital-signage
```

### Obtenir de l'aide

Si vous rencontrez des problèmes:

1. Consultez les logs:
   - Gunicorn: `sudo journalctl -u gunicorn-digital-signage -n 100`
   - Nginx: `sudo tail -n 100 /var/log/nginx/digital-signage-error.log`

2. Vérifiez la configuration:
   - Django: `python manage.py check --deploy`
   - Nginx: `sudo nginx -t`

3. Testez les composants individuellement

---

## Checklist de déploiement

Avant de mettre en production, vérifiez:

- [ ] Le serveur est à jour (`apt update && apt upgrade`)
- [ ] PostgreSQL est installé et configuré
- [ ] Le fichier `.env` est créé et sécurisé (chmod 600)
- [ ] `DEBUG=False` dans le fichier `.env`
- [ ] `SECRET_KEY` est définie et sécurisée
- [ ] `ALLOWED_HOSTS` contient votre domaine
- [ ] Les migrations sont appliquées
- [ ] Les fichiers statiques sont collectés
- [ ] Un superutilisateur est créé
- [ ] Gunicorn démarre correctement
- [ ] Nginx est configuré et fonctionne
- [ ] SSL/HTTPS est configuré avec Let's Encrypt
- [ ] Le firewall (UFW) est activé
- [ ] Les sauvegardes automatiques sont configurées
- [ ] La rotation des logs est configurée
- [ ] L'API répond correctement (test avec curl)
- [ ] L'interface admin est accessible
- [ ] Les écrans peuvent se connecter à l'API

---

## Ressources supplémentaires

- Documentation Django: https://docs.djangoproject.com/
- Documentation Gunicorn: https://docs.gunicorn.org/
- Documentation Nginx: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/
- PostgreSQL: https://www.postgresql.org/docs/

---

**Bon déploiement !** Si vous suivez ce guide étape par étape, votre système sera opérationnel en production.
