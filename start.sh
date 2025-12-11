#!/bin/bash

echo "========================================="
echo "Digital Signage - Démarrage rapide"
echo "========================================="
echo ""

# Vérifier si on est dans le bon dossier
if [ ! -f "manage.py" ]; then
    echo "Erreur: Ce script doit être exécuté depuis le dossier backend/"
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "⚙️  Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  N'oubliez pas de modifier le fichier .env avec vos paramètres!"
fi

# Appliquer les migrations
echo "🗄️  Application des migrations..."
python manage.py makemigrations
python manage.py migrate

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Proposer de créer un superutilisateur
echo ""
read -p "Voulez-vous créer un superutilisateur? (o/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "========================================="
echo "✅ Installation terminée!"
echo "========================================="
echo ""
echo "Pour démarrer le serveur:"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
echo "Accès admin: http://localhost:8000/admin"
echo ""
