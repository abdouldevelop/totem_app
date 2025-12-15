from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.screens.models import Screen
from apps.content.models import Content
from apps.playlists.models import Playlist


@login_required
def dashboard(request):
    """Vue principale du tableau de bord"""

    # Statistiques générales
    total_screens = Screen.objects.count()
    online_screens = Screen.objects.filter(
        last_heartbeat__gte=timezone.now() - timedelta(minutes=5)
    ).count()

    total_content = Content.objects.count()
    active_content = Content.objects.filter(is_active=True).count()

    total_playlists = Playlist.objects.count()
    active_playlists = Playlist.objects.filter(is_active=True).count()

    # Écrans récents
    recent_screens = Screen.objects.all().order_by('-last_heartbeat')[:5]

    # Contenus récents
    recent_content = Content.objects.all().order_by('-created_at')[:5]

    context = {
        'stats': {
            'total_screens': total_screens,
            'online_screens': online_screens,
            'total_content': total_content,
            'active_content': active_content,
            'total_playlists': total_playlists,
            'active_playlists': active_playlists,
            'views_today': 0,  # À implémenter avec analytics
        },
        'recent_screens': recent_screens,
        'recent_content': recent_content,
        'screens_count': total_screens,
    }

    return render(request, 'dashboard.html', context)


@login_required
def analytics(request):
    """Vue de la page analytics"""

    # Statistiques pour les KPIs
    active_playlists_count = Playlist.objects.filter(is_active=True).count()
    scheduled_playlists_count = Playlist.objects.exclude(
        start_date__isnull=True
    ).count()
    total_contents_count = Content.objects.count()
    assigned_screens_count = Screen.objects.exclude(
        Q(playlists__isnull=True)
    ).distinct().count()

    context = {
        'active_playlists_count': active_playlists_count,
        'scheduled_playlists_count': scheduled_playlists_count,
        'total_contents_count': total_contents_count,
        'assigned_screens_count': assigned_screens_count,
    }

    return render(request, 'analytics.html', context)
