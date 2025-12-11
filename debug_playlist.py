#!/usr/bin/env python
"""
Script de diagnostic pour vérifier les playlists assignées aux écrans
"""
import os
import sys
import django

# Configuration de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.screens.models import Screen
from apps.playlists.models import Playlist
from django.utils import timezone

def debug_screen_playlists():
    print("=" * 60)
    print("DIAGNOSTIC DES PLAYLISTS PAR ÉCRAN")
    print("=" * 60)
    print()

    screens = Screen.objects.all()

    if not screens.exists():
        print("❌ Aucun écran trouvé dans la base de données")
        return

    for screen in screens:
        print(f"[ECRAN] {screen.name}")
        print(f"   ID: {screen.id}")
        print(f"   Emplacement: {screen.location}")
        print()

        # Toutes les playlists assignées
        all_playlists = screen.playlists.all()
        print(f"   Playlists assignees: {all_playlists.count()}")

        if all_playlists.count() == 0:
            print("   [!] Aucune playlist assignee a cet ecran")
        else:
            for playlist in all_playlists:
                print(f"   - {playlist.name}")
                print(f"     * Active: {'[OK] Oui' if playlist.is_active else '[NON] Non'}")
                print(f"     * Priorite: {playlist.priority}")

                if playlist.start_date or playlist.end_date:
                    print(f"     * Dates: {playlist.start_date or 'Aucune'} -> {playlist.end_date or 'Aucune'}")

                if playlist.start_time or playlist.end_time:
                    print(f"     * Heures: {playlist.start_time or 'Aucune'} -> {playlist.end_time or 'Aucune'}")

                print(f"     * Jours: {playlist.weekdays}")
                print()

        # Playlists actives seulement
        active_playlists = screen.playlists.filter(is_active=True)
        print(f"   Playlists actives: {active_playlists.count()}")

        # Vérifier les critères de planification
        now = timezone.now()
        current_date = now.date()
        current_time = now.time()
        current_weekday = str(now.weekday())

        print(f"   [DATE] Maintenant: {now.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   [DATE] Date: {current_date}")
        print(f"   [HEURE] Heure: {current_time}")
        print(f"   [JOUR] Jour de la semaine: {current_weekday} (0=Lun, 6=Dim)")
        print()

        # Vérifier quelle playlist devrait être active
        for playlist in active_playlists:
            matches = []

            # Vérifier date de début
            if playlist.start_date:
                if current_date >= playlist.start_date:
                    matches.append("[OK] Date debut OK")
                else:
                    matches.append(f"[X] Date debut NOK (commence le {playlist.start_date})")
            else:
                matches.append("[OK] Pas de date debut")

            # Vérifier date de fin
            if playlist.end_date:
                if current_date <= playlist.end_date:
                    matches.append("[OK] Date fin OK")
                else:
                    matches.append(f"[X] Date fin NOK (terminee le {playlist.end_date})")
            else:
                matches.append("[OK] Pas de date fin")

            # Vérifier heure de début
            if playlist.start_time:
                if current_time >= playlist.start_time:
                    matches.append("[OK] Heure debut OK")
                else:
                    matches.append(f"[X] Heure debut NOK (commence a {playlist.start_time})")
            else:
                matches.append("[OK] Pas d'heure debut")

            # Vérifier heure de fin
            if playlist.end_time:
                if current_time <= playlist.end_time:
                    matches.append("[OK] Heure fin OK")
                else:
                    matches.append(f"[X] Heure fin NOK (termine a {playlist.end_time})")
            else:
                matches.append("[OK] Pas d'heure fin")

            # Vérifier jour de la semaine
            if playlist.weekdays:
                if current_weekday in playlist.weekdays:
                    matches.append("[OK] Jour de la semaine OK")
                else:
                    matches.append(f"[X] Jour de la semaine NOK (jours autorises: {playlist.weekdays})")
            else:
                matches.append("[OK] Tous les jours")

            print(f"   [PLAYLIST] {playlist.name}")
            for match in matches:
                print(f"      {match}")

            all_ok = all("[OK]" in match for match in matches)
            if all_ok:
                print(f"      >>> Cette playlist DEVRAIT etre affichee")
            else:
                print(f"      >>> Cette playlist NE SERA PAS affichee")
            print()

        print("-" * 60)
        print()

if __name__ == '__main__':
    debug_screen_playlists()
