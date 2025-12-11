# Digital Signage - Guide Rapide de Déploiement

Ce document est un résumé pour déployer rapidement votre système Digital Signage en production.

## Fichiers de Déploiement Disponibles

Votre projet contient tous les fichiers nécessaires pour le déploiement:

```
backend/
├── DEPLOYMENT_GUIDE.md          # Guide détaillé étape par étape
├── PRE_DEPLOYMENT_CHECKLIST.md  # Checklist de vérification
├── HEROKU_QUICKSTART.md          # Guide pour Heroku
├── deploy.sh                     # Script de déploiement/mise à jour
├── install_server.sh             # Installation automatique du serveur
├── .env.example                  # Modèle pour environnement de dev
├── .env.production               # Modèle pour production
├── gunicorn.service.example      # Configuration systemd pour Gunicorn
├── nginx.conf.example            # Configuration Nginx
├── requirements.txt              # Dépendances Python
├── Procfile                      # Configuration Heroku
└── runtime.txt                   # Version Python pour Heroku
```

---

## Méthode 1: Installation Automatique (RECOMMANDÉ)

La méthode la plus simple pour déployer sur un serveur Linux.

### Prérequis
- Un serveur Ubuntu 22.04 ou Debian 11+
- Accès SSH avec droits sudo
- Un nom de domaine pointant vers votre serveur

### Étapes

1. **Connectez-vous à votre serveur**
   ```bash
   ssh votre-utilisateur@votre-serveur.com
   ```

2. **Transférez le script d'installation**
   Depuis votre machine locale:
   ```bash
   scp backend/install_server.sh votre-utilisateur@votre-serveur.com:~/
   ```

3. **Exécutez le script**
   Sur le serveur:
   ```bash
   chmod +x install_server.sh
   sudo ./install_server.sh
   ```

4. **Suivez les instructions du script**
   Le script vous demandera:
   - Votre nom de domaine
   - Un mot de passe pour PostgreSQL
   - Votre nom d'utilisateur système

5. **Transférez votre code**
   Depuis votre machine locale:
   ```bash
   cd backend
   scp -r * votre-utilisateur@votre-serveur.com:/opt/digital_signage/
   ```

6. **Finalisez l'installation**
   Sur le serveur:
   ```bash
   cd /opt/digital_signage
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   sudo systemctl start gunicorn.socket
   ```

7. **Configurez SSL**
   ```bash
   sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
   ```

**Terminé !** Votre application est en ligne sur https://votre-domaine.com

---

## Méthode 2: Déploiement sur Heroku

Pour un déploiement rapide sans gérer de serveur.

### Étapes rapides

```bash
# 1. Installer Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Se connecter
heroku login

# 3. Créer l'application
heroku create nom-de-votre-app

# 4. Ajouter PostgreSQL
heroku addons:create heroku-postgresql:mini

# 5. Configurer les variables d'environnement
heroku config:set SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=nom-de-votre-app.herokuapp.com

# 6. Déployer
git push heroku main

# 7. Migrer la base de données
heroku run python manage.py migrate

# 8. Créer un superutilisateur
heroku run python manage.py createsuperuser

# 9. Ouvrir l'application
heroku open
```

Pour plus de détails, consultez `HEROKU_QUICKSTART.md`.

---

## Méthode 3: Installation Manuelle

Pour un contrôle total de chaque étape.

### 1. Préparation
Consultez `PRE_DEPLOYMENT_CHECKLIST.md` et préparez:
- Informations du serveur
- Nom de domaine
- Mots de passe sécurisés
- SECRET_KEY Django

### 2. Déploiement
Suivez le guide détaillé dans `DEPLOYMENT_GUIDE.md` section "Déploiement sur serveur Linux"

### 3. Vérification
Utilisez `PRE_DEPLOYMENT_CHECKLIST.md` pour vérifier chaque étape

---

## Mise à Jour de l'Application

### Avec le script de déploiement
```bash
cd /opt/digital_signage
./deploy.sh
```

### Manuellement
```bash
cd /opt/digital_signage
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-digital-signage
```

---

## Configuration de l'Application Mobile

Après avoir déployé le backend, configurez l'application mobile pour pointer vers votre serveur.

### Modifier l'API URL

1. Ouvrez `mobile/src/config.js` (ou le fichier de configuration approprié)

2. Changez l'URL de l'API:
   ```javascript
   export const API_URL = 'https://votre-domaine.com/api';
   ```

3. Rebuilder l'application mobile:
   ```bash
   cd mobile
   npm run build
   ```

---

## Commandes Utiles

### Gestion des services
```bash
# Redémarrer l'application
sudo systemctl restart gunicorn-digital-signage

# Voir les logs
sudo journalctl -u gunicorn-digital-signage -f

# Vérifier le statut
sudo systemctl status gunicorn-digital-signage
sudo systemctl status nginx
```

### Gestion Django
```bash
cd /opt/digital_signage
source venv/bin/activate

# Créer un superutilisateur
python manage.py createsuperuser

# Vérifier la configuration
python manage.py check --deploy

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### Sauvegardes
```bash
# Sauvegarder la base de données
pg_dump digital_signage_prod > backup_$(date +%Y%m%d).sql

# Restaurer une sauvegarde
psql digital_signage_prod < backup_20231211.sql
```

---

## Dépannage Rapide

### L'application ne démarre pas
```bash
sudo journalctl -u gunicorn-digital-signage -n 50
python manage.py check
```

### Erreur 502 Bad Gateway
```bash
sudo systemctl status gunicorn-digital-signage
sudo systemctl restart gunicorn-digital-signage
```

### Les fichiers statiques ne se chargent pas
```bash
python manage.py collectstatic --noinput --clear
sudo systemctl restart nginx
```

### Erreur de base de données
```bash
sudo systemctl status postgresql
# Vérifier le fichier .env
cat .env
```

Pour plus de solutions, consultez la section "Dépannage" dans `DEPLOYMENT_GUIDE.md`

---

## Architecture de Production

Votre application déployée utilisera:

```
Internet
    ↓
[Nginx] ← Serveur web, SSL, fichiers statiques
    ↓
[Gunicorn] ← Serveur d'application Python (4 workers)
    ↓
[Django] ← Application backend
    ↓
[PostgreSQL] ← Base de données
```

---

## Sécurité

Vérifiez que:
- [ ] `DEBUG=False` en production
- [ ] SSL/HTTPS configuré
- [ ] SECRET_KEY unique et sécurisée
- [ ] Mots de passe forts
- [ ] Firewall activé
- [ ] Sauvegardes automatiques configurées

---

## Ressources

- **Guide détaillé**: `DEPLOYMENT_GUIDE.md`
- **Checklist**: `PRE_DEPLOYMENT_CHECKLIST.md`
- **Heroku**: `HEROKU_QUICKSTART.md`

---

## Support

En cas de problème:

1. Consultez les logs:
   ```bash
   sudo journalctl -u gunicorn-digital-signage -n 100
   sudo tail -n 100 /var/log/nginx/digital-signage-error.log
   ```

2. Vérifiez la configuration:
   ```bash
   python manage.py check --deploy
   sudo nginx -t
   ```

3. Consultez le guide de dépannage dans `DEPLOYMENT_GUIDE.md`

---

**Prêt à déployer ?**

1. Lisez `PRE_DEPLOYMENT_CHECKLIST.md`
2. Préparez vos informations (domaine, serveur, mots de passe)
3. Choisissez votre méthode de déploiement
4. Suivez le guide correspondant

**Bon déploiement !**
