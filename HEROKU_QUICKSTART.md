# 🚀 Déploiement Rapide sur Heroku

Guide ultra-court pour déployer en 10 minutes.

---

## Étape 1: Installer Heroku CLI

**Windows:**
- Télécharger: https://devcenter.heroku.com/articles/heroku-cli
- Installer et vérifier:
  ```cmd
  heroku --version
  ```

---

## Étape 2: Se Connecter

```bash
heroku login
# Cliquez "Log in" dans le navigateur
```

---

## Étape 3: Créer l'App

```bash
cd C:\Programme\digital_signage_project\backend

# Créer l'app (choisissez un nom unique)
heroku create signage-votrenom

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:essential-0
```

---

## Étape 4: Configurer les Variables

```bash
# Générer une SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configurer (remplacer XXX par la clé générée)
heroku config:set SECRET_KEY="XXX"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=".herokuapp.com"
```

---

## Étape 5: Déployer

```bash
# Initialiser Git si nécessaire
git init
git add .
git commit -m "Deploy to Heroku"

# Pousser vers Heroku
git push heroku main

# Attendre 2-3 minutes...
```

---

## Étape 6: Setup Initial

```bash
# Créer un admin
heroku run python manage.py createsuperuser

# Ouvrir l'app
heroku open
```

---

## Étape 7: Configurer l'App Mobile

1. **Éditer `mobile/src/config.js`:**
   ```javascript
   const ENVIRONMENT = 'production';

   const ENVIRONMENTS = {
     production: {
       API_BASE_URL: 'https://votre-app.herokuapp.com',
     },
   };
   ```

2. **Recompiler l'APK:**
   ```bash
   cd mobile
   npm run build:apk
   ```

---

## ✅ C'est Fini!

**Votre app:** https://votre-app.herokuapp.com

**Tester:**
```bash
# Voir les logs
heroku logs --tail

# Tester l'API
curl https://votre-app.herokuapp.com/api/screens/register/
```

---

## 🆘 Problèmes?

```bash
# Voir les erreurs
heroku logs --tail

# Redémarrer
heroku restart

# Plus d'aide dans GUIDE_DEPLOIEMENT_HEROKU.md
```
