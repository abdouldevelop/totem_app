#!/usr/bin/env python
"""
Script de diagnostic pour vérifier la configuration Digital Signage
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.screens.models import Screen
from apps.playlists.models import Playlist, PlaylistItem
from apps.content.models import Content
from django.utils import timezone

def check_setup():
    print("=" * 60)
    print("DIAGNOSTIC DIGITAL SIGNAGE")
    print("=" * 60)
    print()

    # 1. Vérifier les écrans
    print("1. ÉCRANS ENREGISTRÉS")
    print("-" * 60)
    screens = Screen.objects.all()
    if screens.exists():
        for screen in screens:
            print(f"✓ {screen.name} (ID: {screen.id})")
            print(f"  Status: {screen.status}")
            print(f"  Dernier heartbeat: {screen.last_heartbeat or 'Jamais'}")
            print()
    else:
        print("✗ Aucun écran enregistré")
        print()

    # 2. Vérifier les contenus
    print("2. CONTENUS DISPONIBLES")
    print("-" * 60)
    contents = Content.objects.all()
    if contents.exists():
        for content in contents:
            status_icon = "✓" if content.is_active else "✗"
            print(f"{status_icon} {content.title}")
            print(f"  Type: {content.content_type}")
            print(f"  Actif: {'Oui' if content.is_active else 'Non'}")
            print(f"  Durée: {content.duration}s")
            print()
    else:
        print("✗ Aucun contenu créé")
        print("  → Allez dans l'admin: Contenus → Ajouter")
        print()

    # 3. Vérifier les playlists
    print("3. PLAYLISTS CONFIGURÉES")
    print("-" * 60)
    playlists = Playlist.objects.all()
    if playlists.exists():
        for playlist in playlists:
            status_icon = "✓" if playlist.is_active else "✗"
            print(f"{status_icon} {playlist.name}")
            print(f"  Active: {'Oui' if playlist.is_active else 'Non'}")
            print(f"  Jours: {playlist.weekdays}")
            print(f"  Écrans assignés: {playlist.screens.count()}")

            # Vérifier les items
            items = playlist.items.all()
            if items.exists():
                print(f"  Contenus ({items.count()}):")
                for item in items:
                    active_icon = "✓" if item.content.is_active else "✗"
                    print(f"    {active_icon} {item.content.title} ({item.content.content_type})")
            else:
                print(f"  ✗ Aucun contenu dans cette playlist")
                print(f"    → Éditez la playlist et ajoutez des contenus dans 'Items'")
            print()
    else:
        print("✗ Aucune playlist créée")
        print("  → Allez dans l'admin: Playlists → Ajouter")
        print()

    # 4. Vérifier la configuration pour chaque écran
    print("4. CONFIGURATION PAR ÉCRAN")
    print("-" * 60)
    now = timezone.now()
    current_date = now.date()
    current_time = now.time()
    current_weekday = str(now.weekday())

    print(f"Jour actuel: {current_weekday} ({['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][now.weekday()]})")
    print(f"Heure actuelle: {current_time.strftime('%H:%M:%S')}")
    print()

    for screen in screens:
        print(f"Écran: {screen.name}")

        # Trouver la playlist active
        active_playlists = Playlist.objects.filter(
            screens=screen,
            is_active=True
        ).filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=current_date)
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=current_date)
        ).filter(
            models.Q(start_time__isnull=True) | models.Q(start_time__lte=current_time)
        ).filter(
            models.Q(end_time__isnull=True) | models.Q(end_time__gte=current_time)
        ).filter(
            weekdays__contains=current_weekday
        )

        if active_playlists.exists():
            playlist = active_playlists.first()
            print(f"  ✓ Playlist active: {playlist.name}")
            items = playlist.items.filter(content__is_active=True)
            if items.exists():
                print(f"  ✓ {items.count()} contenu(s) à afficher")
            else:
                print(f"  ✗ La playlist est vide ou les contenus sont inactifs")
        else:
            print(f"  ✗ Aucune playlist active pour cet écran")

            # Diagnostiquer pourquoi
            all_playlists = screen.playlists.all()
            if not all_playlists.exists():
                print(f"    → Raison: Aucune playlist assignée à cet écran")
                print(f"    → Solution: Éditez une playlist et assignez-la à '{screen.name}'")
            else:
                for pl in all_playlists:
                    reasons = []
                    if not pl.is_active:
                        reasons.append("Playlist désactivée")
                    if pl.start_date and pl.start_date > current_date:
                        reasons.append(f"Commence le {pl.start_date}")
                    if pl.end_date and pl.end_date < current_date:
                        reasons.append(f"Terminée le {pl.end_date}")
                    if current_weekday not in pl.weekdays.split(','):
                        reasons.append(f"Jour actuel ({current_weekday}) non inclus dans {pl.weekdays}")

                    if reasons:
                        print(f"    Playlist '{pl.name}': {', '.join(reasons)}")
        print()

    # 5. Recommandations
    print("5. RECOMMANDATIONS")
    print("-" * 60)

    if not screens.exists():
        print("⚠ Lancez l'application mobile et enregistrez un écran")

    if not contents.exists():
        print("⚠ Créez au moins un contenu (image, vidéo, ou web)")
        print("  Admin → Contenus → Ajouter")

    if not playlists.exists():
        print("⚠ Créez une playlist")
        print("  Admin → Playlists → Ajouter")
    else:
        for playlist in playlists:
            if not playlist.items.exists():
                print(f"⚠ Ajoutez des contenus à la playlist '{playlist.name}'")
                print(f"  Admin → Playlists → {playlist.name} → Section 'Items'")

            if not playlist.screens.exists():
                print(f"⚠ Assignez la playlist '{playlist.name}' à un écran")
                print(f"  Admin → Playlists → {playlist.name} → Section 'Écrans'")

    print()
    print("=" * 60)
    print("FIN DU DIAGNOSTIC")
    print("=" * 60)

if __name__ == '__main__':
    from django.db import models
    check_setup()
