# Checklist de Pré-Déploiement
# Digital Signage Backend

Cette checklist vous aide à vérifier que tout est prêt avant le déploiement en production.

## Informations à préparer AVANT le déploiement

### Informations serveur
- [ ] Adresse IP du serveur: ___________________
- [ ] Nom d'utilisateur SSH: ___________________
- [ ] Mot de passe ou clé SSH configurée
- [ ] Accès sudo disponible

### Informations domaine
- [ ] Nom de domaine: ___________________
- [ ] DNS configuré (domaine pointe vers le serveur)
- [ ] Temps de propagation DNS respecté (24-48h)

### Informations base de données
- [ ] Nom de la base: ___________________
- [ ] Utilisateur DB: ___________________
- [ ] Mot de passe DB (généré et sécurisé): ___________________

### Informations Django
- [ ] SECRET_KEY générée (utilisez la commande ci-dessous)
- [ ] Liste des ALLOWED_HOSTS préparée

---

## Génération des informations sensibles

### Générer une SECRET_KEY
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copiez la clé générée: ___________________

### Générer un mot de passe PostgreSQL sécurisé
```bash
openssl rand -base64 32
```

Copiez le mot de passe: ___________________

---

## Vérifications locales (avant transfert)

### Code source
- [ ] Toutes les modifications sont committées
- [ ] Le code est testé localement
- [ ] Aucun fichier sensible dans le dépôt (.env, secrets, etc.)
- [ ] Le fichier .gitignore est correctement configuré

### Configuration
- [ ] `requirements.txt` est à jour
- [ ] `.env.example` et `.env.production` sont présents
- [ ] Les fichiers de déploiement sont présents:
  - [ ] `deploy.sh`
  - [ ] `install_server.sh`
  - [ ] `gunicorn.service.example`
  - [ ] `nginx.conf.example`

### Documentation
- [ ] `DEPLOYMENT_GUIDE.md` est à jour
- [ ] `README.md` contient les instructions de base
- [ ] `HEROKU_QUICKSTART.md` est présent (si applicable)

---

## Vérifications sur le serveur

### Système
- [ ] Serveur accessible via SSH
- [ ] Système à jour: `sudo apt update && sudo apt upgrade -y`
- [ ] Espace disque suffisant: `df -h`
- [ ] RAM disponible: `free -h`

### Installation automatique (RECOMMANDÉ)
- [ ] Script `install_server.sh` transféré sur le serveur
- [ ] Script rendu exécutable: `chmod +x install_server.sh`
- [ ] Script exécuté avec succès: `sudo ./install_server.sh`

OU (si installation manuelle)

### Dépendances installées
- [ ] Python 3.8+ installé: `python3 --version`
- [ ] pip installé: `pip3 --version`
- [ ] PostgreSQL installé: `psql --version`
- [ ] Nginx installé: `nginx -v`
- [ ] Git installé: `git --version`
- [ ] Certbot installé: `certbot --version`

### Base de données
- [ ] PostgreSQL démarre: `sudo systemctl status postgresql`
- [ ] Base de données créée
- [ ] Utilisateur DB créé avec les bons privilèges
- [ ] Connexion testée: `psql -U signage_user -d digital_signage_prod`

### Répertoire projet
- [ ] Répertoire `/opt/digital_signage` créé
- [ ] Permissions correctes: `ls -la /opt/digital_signage`
- [ ] Code source transféré

---

## Configuration de l'application

### Environnement Python
- [ ] Environnement virtuel créé: `python3 -m venv venv`
- [ ] Environnement activé: `source venv/bin/activate`
- [ ] pip mis à jour: `pip install --upgrade pip`
- [ ] Dépendances installées: `pip install -r requirements.txt`

### Fichier .env
- [ ] Fichier `.env` créé (copie de `.env.production`)
- [ ] `SECRET_KEY` définie et unique
- [ ] `DEBUG=False` (IMPORTANT!)
- [ ] `ALLOWED_HOSTS` configuré avec le domaine et l'IP
- [ ] Informations DB correctes
- [ ] `CORS_ALLOWED_ORIGINS` configuré
- [ ] Permissions: `chmod 600 .env`

### Django
- [ ] Migrations appliquées: `python manage.py migrate`
- [ ] Pas d'erreurs dans les migrations
- [ ] Superutilisateur créé: `python manage.py createsuperuser`
- [ ] Fichiers statiques collectés: `python manage.py collectstatic --noinput`
- [ ] Vérification Django: `python manage.py check --deploy`

### Dossiers
- [ ] Dossier `media` créé
- [ ] Dossier `staticfiles` créé
- [ ] Dossier `/opt/backups` créé
- [ ] Permissions correctes: `chmod 755 media staticfiles`

---

## Configuration des services

### Gunicorn
- [ ] Dossier logs créé: `sudo mkdir -p /var/log/gunicorn`
- [ ] Fichier service créé: `/etc/systemd/system/gunicorn-digital-signage.service`
- [ ] Chemins remplacés dans le fichier service
- [ ] Utilisateur correct dans le fichier service
- [ ] Daemon rechargé: `sudo systemctl daemon-reload`
- [ ] Service démarré: `sudo systemctl start gunicorn-digital-signage`
- [ ] Service activé: `sudo systemctl enable gunicorn-digital-signage`
- [ ] Statut OK: `sudo systemctl status gunicorn-digital-signage`

### Nginx
- [ ] Configuration créée: `/etc/nginx/sites-available/digital-signage`
- [ ] Domaine remplacé dans la configuration
- [ ] Chemins remplacés dans la configuration
- [ ] Lien symbolique créé: `/etc/nginx/sites-enabled/digital-signage`
- [ ] Configuration par défaut désactivée
- [ ] Test configuration: `sudo nginx -t` (doit être OK)
- [ ] Service redémarré: `sudo systemctl restart nginx`
- [ ] Service activé: `sudo systemctl enable nginx`

### SSL/HTTPS
- [ ] Let's Encrypt installé: `certbot --version`
- [ ] Certificat obtenu: `sudo certbot --nginx -d votre-domaine.com`
- [ ] Redirection HTTP vers HTTPS configurée
- [ ] Test renouvellement: `sudo certbot renew --dry-run`

### Firewall
- [ ] UFW installé
- [ ] UFW activé: `sudo ufw --force enable`
- [ ] SSH autorisé: `sudo ufw allow ssh`
- [ ] Nginx autorisé: `sudo ufw allow 'Nginx Full'`
- [ ] Statut vérifié: `sudo ufw status`

---

## Tests de fonctionnement

### Tests basiques
- [ ] L'application répond: `curl http://localhost:8000/api/`
- [ ] L'API répond via le domaine: `curl https://votre-domaine.com/api/`
- [ ] L'interface admin est accessible: https://votre-domaine.com/admin/
- [ ] Connexion admin fonctionne
- [ ] HTTPS fonctionne (pas d'erreur de certificat)
- [ ] Redirection HTTP vers HTTPS fonctionne

### Tests des logs
- [ ] Logs Gunicorn accessibles: `sudo journalctl -u gunicorn-digital-signage -n 20`
- [ ] Aucune erreur critique dans les logs
- [ ] Logs Nginx accessibles: `sudo tail -n 20 /var/log/nginx/digital-signage-access.log`

### Tests des fichiers statiques
- [ ] Page admin charge correctement (avec CSS)
- [ ] Fichiers statiques servis par Nginx
- [ ] Test d'upload de média fonctionne

### Tests CORS
- [ ] Une requête depuis l'origine autorisée fonctionne
- [ ] Tester avec un outil comme Postman ou curl:
```bash
curl -H "Origin: https://votre-domaine.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS --verbose \
     https://votre-domaine.com/api/
```

---

## Configuration post-déploiement

### Sauvegardes
- [ ] Script de sauvegarde créé: `/opt/backups/backup_db.sh`
- [ ] Script testé manuellement
- [ ] Tâche cron configurée pour sauvegardes automatiques
- [ ] Vérifier que les sauvegardes se créent: `ls -lh /opt/backups/`

### Rotation des logs
- [ ] Configuration logrotate créée: `/etc/logrotate.d/digital-signage`
- [ ] Configuration testée: `sudo logrotate -d /etc/logrotate.d/digital-signage`

### Surveillance
- [ ] Outil de surveillance installé (htop, glances, etc.)
- [ ] Alertes configurées (optionnel)

### Documentation
- [ ] Informations de connexion sauvegardées en lieu sûr
- [ ] Mots de passe stockés dans un gestionnaire de mots de passe
- [ ] Documentation d'exploitation créée

---

## Tests de charge (optionnel mais recommandé)

### Test de performance basique
```bash
# Installer Apache Bench
sudo apt install apache2-utils

# Tester 100 requêtes avec 10 connexions concurrentes
ab -n 100 -c 10 https://votre-domaine.com/api/
```

- [ ] Le serveur répond sans erreur
- [ ] Temps de réponse acceptable
- [ ] Pas d'erreur 500 ou 502

---

## Checklist finale avant mise en production

### Sécurité
- [ ] `DEBUG=False` dans .env
- [ ] SECRET_KEY unique et sécurisée
- [ ] Mots de passe forts et sécurisés
- [ ] Fichier .env avec permissions 600
- [ ] Firewall activé
- [ ] SSL/HTTPS configuré
- [ ] Headers de sécurité configurés dans Nginx

### Fonctionnalités
- [ ] API accessible et fonctionnelle
- [ ] Interface admin accessible
- [ ] Authentification fonctionne
- [ ] Upload de fichiers fonctionne
- [ ] Base de données répond correctement

### Services
- [ ] Gunicorn démarre et reste actif
- [ ] Nginx démarre et reste actif
- [ ] PostgreSQL démarre et reste actif
- [ ] Tous les services activés au démarrage

### Monitoring
- [ ] Logs accessibles et lisibles
- [ ] Sauvegardes configurées
- [ ] Rotation des logs configurée
- [ ] Surveillance en place

### Documentation
- [ ] Guide de déploiement suivi
- [ ] Informations de connexion sauvegardées
- [ ] Procédures de maintenance documentées

---

## Commandes de vérification rapide

Exécutez ces commandes pour une vérification globale:

```bash
# Statut des services
sudo systemctl status gunicorn-digital-signage
sudo systemctl status nginx
sudo systemctl status postgresql

# Vérification Django
cd /opt/digital_signage
source venv/bin/activate
python manage.py check --deploy

# Test API
curl https://votre-domaine.com/api/

# Logs récents
sudo journalctl -u gunicorn-digital-signage -n 20 --no-pager

# Espace disque
df -h

# Mémoire
free -h

# Processus Gunicorn
ps aux | grep gunicorn
```

---

## En cas de problème

Si quelque chose ne fonctionne pas:

1. Consultez le guide de dépannage dans `DEPLOYMENT_GUIDE.md`
2. Vérifiez les logs:
   - Gunicorn: `sudo journalctl -u gunicorn-digital-signage -n 50`
   - Nginx: `sudo tail -n 50 /var/log/nginx/digital-signage-error.log`
3. Vérifiez la configuration:
   - Django: `python manage.py check --deploy`
   - Nginx: `sudo nginx -t`

---

## Après le déploiement

### Actions immédiates
- [ ] Tester l'application complètement
- [ ] Vérifier les logs pour les erreurs
- [ ] Créer une sauvegarde initiale
- [ ] Documenter les problèmes rencontrés

### Dans les 24 heures
- [ ] Surveiller les logs
- [ ] Vérifier les performances
- [ ] Tester toutes les fonctionnalités critiques
- [ ] Vérifier que les sauvegardes automatiques fonctionnent

### Dans la semaine
- [ ] Former les utilisateurs
- [ ] Documenter les procédures spécifiques
- [ ] Planifier la maintenance
- [ ] Évaluer les performances sous charge réelle

---

**Félicitations !** Si toutes les cases sont cochées, votre application est prête pour la production !

Pour toute question, consultez `DEPLOYMENT_GUIDE.md` ou les ressources listées à la fin du guide.
