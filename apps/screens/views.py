from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import Screen
from .serializers import ScreenSerializer, ScreenRegisterSerializer
from apps.playlists.models import Playlist
from apps.playlists.serializers import PlaylistSerializer
from apps.analytics.models import ScreenLog
import uuid


class ScreenViewSet(viewsets.ModelViewSet):
    queryset = Screen.objects.all()
    serializer_class = ScreenSerializer
    
    def get_permissions(self):
        # Autoriser l'enregistrement sans authentification
        if self.action == 'register':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Enregistrement initial d'un nouvel écran"""
        serializer = ScreenRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device_info = serializer.validated_data.get('device_info', {})
        app_version = serializer.validated_data.get('app_version', '1.0.0')
        
        screen = Screen.objects.create(
            name=f"Écran {Screen.objects.count() + 1}",
            location="À définir",
            api_token=str(uuid.uuid4()),
            device_info=device_info,
            app_version=app_version,
            status='active',
            last_heartbeat=timezone.now()
        )
        
        return Response({
            'screen_id': str(screen.id),
            'api_token': screen.api_token,
            'name': screen.name,
            'location': screen.location
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def heartbeat(self, request):
        """Signale que l'écran est actif"""
        token = request.META.get('HTTP_X_SCREEN_TOKEN')
        if not token:
            return Response({'error': 'Token manquant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            screen = Screen.objects.get(api_token=token)
            screen.last_heartbeat = timezone.now()
            screen.status = 'active'
            
            # Mettre à jour les infos si fournies
            if 'app_version' in request.data:
                screen.app_version = request.data['app_version']
            if 'device_info' in request.data:
                screen.device_info = request.data['device_info']
            
            screen.save(update_fields=['last_heartbeat', 'status', 'app_version', 'device_info'])
            
            return Response({
                'status': 'ok',
                'screen_id': str(screen.id),
                'name': screen.name
            })
        except Screen.DoesNotExist:
            return Response({'error': 'Écran non trouvé'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def current_playlist(self, request):
        """Retourne la playlist active pour cet écran"""
        token = request.META.get('HTTP_X_SCREEN_TOKEN')
        if not token:
            return Response({'error': 'Token manquant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            screen = Screen.objects.get(api_token=token)
            
            # Trouve la playlist active pour cet écran
            now = timezone.now()
            current_date = now.date()
            current_time = now.time()
            current_weekday = str(now.weekday())
            
            playlist = Playlist.objects.filter(
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
            ).order_by('-priority').first()
            
            if playlist:
                serializer = PlaylistSerializer(playlist, context={'request': request})
                return Response(serializer.data)
            
            return Response({'message': 'Aucune playlist active'}, 
                          status=status.HTTP_204_NO_CONTENT)
            
        except Screen.DoesNotExist:
            return Response({'error': 'Écran non trouvé'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def log_event(self, request):
        """Log des événements depuis l'écran"""
        token = request.META.get('HTTP_X_SCREEN_TOKEN')
        if not token:
            return Response({'error': 'Token manquant'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            screen = Screen.objects.get(api_token=token)
            
            ScreenLog.objects.create(
                screen=screen,
                content_id=request.data.get('content_id'),
                action=request.data.get('action', 'unknown'),
                details=request.data.get('details', {})
            )
            
            return Response({'status': 'logged'})
        except Screen.DoesNotExist:
            return Response({'error': 'Écran non trouvé'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def status_detail(self, request, pk=None):
        """Détails du statut d'un écran"""
        screen = self.get_object()
        recent_logs = screen.logs.all()[:10]

        return Response({
            'screen': ScreenSerializer(screen).data,
            'is_online': screen.is_online(),
            'playlists': PlaylistSerializer(screen.playlists.filter(is_active=True), many=True).data,
            'recent_logs': [
                {
                    'action': log.action,
                    'timestamp': log.timestamp,
                    'details': log.details
                } for log in recent_logs
            ]
        })


# =============================================================================
# VUES WEB POUR LES TEMPLATES HTML
# =============================================================================

@login_required
def screens_list(request):
    """Liste de tous les écrans"""
    screens = Screen.objects.all().order_by('-last_heartbeat')

    # Ajouter la propriété is_online pour chaque écran
    for screen in screens:
        screen.is_online = screen.last_heartbeat and (
            timezone.now() - screen.last_heartbeat < timedelta(minutes=5)
        )

    context = {
        'screens': screens,
        'screens_count': screens.count(),
    }

    return render(request, 'screens/list.html', context)


@login_required
def screen_detail(request, pk):
    """Détails d'un écran spécifique"""
    screen = get_object_or_404(Screen, pk=pk)

    # Vérifier si l'écran est en ligne
    screen.is_online = screen.last_heartbeat and (
        timezone.now() - screen.last_heartbeat < timedelta(minutes=5)
    )

    # Récupérer les logs récents
    screen_logs = ScreenLog.objects.filter(screen=screen).order_by('-timestamp')[:20]

    # Playlist actuelle
    current_playlist = None
    try:
        # D'abord, chercher toutes les playlists assignées à cet écran
        assigned_playlists = screen.playlists.filter(is_active=True)

        if assigned_playlists.exists():
            # Si on a des playlists, appliquer les filtres de planification
            now = timezone.now()
            current_date = now.date()
            current_time = now.time()
            current_weekday = str(now.weekday())

            # Chercher une playlist qui correspond aux critères de planification
            current_playlist = assigned_playlists.filter(
                models.Q(start_date__isnull=True) | models.Q(start_date__lte=current_date)
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=current_date)
            ).filter(
                models.Q(start_time__isnull=True) | models.Q(start_time__lte=current_time)
            ).filter(
                models.Q(end_time__isnull=True) | models.Q(end_time__gte=current_time)
            ).filter(
                models.Q(weekdays__isnull=True) | models.Q(weekdays__contains=current_weekday)
            ).order_by('-priority').first()

            # Si aucune playlist ne correspond aux critères de planification,
            # prendre la première playlist active assignée (fallback)
            if not current_playlist:
                current_playlist = assigned_playlists.order_by('-priority').first()
    except Exception as e:
        print(f"Erreur lors de la récupération de la playlist: {e}")

    screen.current_playlist = current_playlist

    context = {
        'screen': screen,
        'screen_logs': screen_logs,
        'screens_count': Screen.objects.count(),
    }

    return render(request, 'screens/detail.html', context)


@login_required
def screen_create(request):
    """Formulaire de création d'un écran"""
    from django.contrib import messages

    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.POST.get('name')
        location = request.POST.get('location', '')
        description = request.POST.get('description', '')

        # Générer un token unique
        api_token = str(uuid.uuid4())

        # Créer l'écran
        screen = Screen.objects.create(
            name=name,
            location=location,
            description=description,
            api_token=api_token,
            status='inactive'  # Inactif jusqu'à ce que l'app se connecte
        )

        messages.success(request, f'L\'écran "{name}" a été créé avec succès ! Token: {api_token}')
        return redirect('screen_detail', pk=screen.pk)

    context = {
        'screens_count': Screen.objects.count(),
    }

    return render(request, 'screens/create.html', context)


@login_required
def screen_edit(request, pk):
    """Formulaire d'édition d'un écran"""
    from django.contrib import messages
    screen = get_object_or_404(Screen, pk=pk)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        screen.name = request.POST.get('name')
        screen.location = request.POST.get('location')
        screen.description = request.POST.get('description', '')
        screen.status = request.POST.get('status', 'active')

        screen.save()

        messages.success(request, f'L\'écran "{screen.name}" a été modifié avec succès !')
        return redirect('screen_detail', pk=screen.pk)

    context = {
        'screen': screen,
        'screens_count': Screen.objects.count(),
    }

    return render(request, 'screens/edit.html', context)


@login_required
def screen_assign_playlist(request, pk):
    """Assigner ou changer la playlist d'un écran"""
    from django.contrib import messages
    from apps.playlists.models import Playlist

    screen = get_object_or_404(Screen, pk=pk)

    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')
        if playlist_id:
            try:
                playlist = Playlist.objects.get(id=playlist_id)
                # Ajouter l'écran à la playlist
                playlist.screens.add(screen)
                messages.success(request, f'La playlist "{playlist.name}" a été assignée à l\'écran "{screen.name}".')
            except Playlist.DoesNotExist:
                messages.error(request, 'Playlist non trouvée.')
        return redirect('screen_detail', pk=screen.pk)

    # GET request - afficher le formulaire
    playlists = Playlist.objects.filter(is_active=True).order_by('-created_at')

    context = {
        'screen': screen,
        'playlists': playlists,
        'screens_count': Screen.objects.count(),
    }

    return render(request, 'screens/assign_playlist.html', context)


@login_required
def screen_restart(request, pk):
    """Redémarrer un écran"""
    from django.contrib import messages
    from django.http import JsonResponse

    screen = get_object_or_404(Screen, pk=pk)

    # Créer un log pour le redémarrage
    ScreenLog.objects.create(
        screen=screen,
        action='restart_requested',
        details={'requested_by': request.user.username}
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Commande de redémarrage envoyée'})

    messages.success(request, f'Commande de redémarrage envoyée à l\'écran "{screen.name}".')
    return redirect('screen_detail', pk=screen.pk)


@login_required
def screen_logs(request, pk):
    """Afficher tous les logs d'un écran"""
    screen = get_object_or_404(Screen, pk=pk)

    # Récupérer tous les logs de cet écran
    logs = ScreenLog.objects.filter(screen=screen).order_by('-timestamp')

    context = {
        'screen': screen,
        'logs': logs,
        'screens_count': Screen.objects.count(),
    }

    return render(request, 'screens/logs.html', context)


@login_required
def screen_download_logs(request, pk):
    """Télécharger les logs d'un écran en CSV"""
    from django.http import HttpResponse
    import csv

    screen = get_object_or_404(Screen, pk=pk)
    logs = ScreenLog.objects.filter(screen=screen).order_by('-timestamp')

    # Créer la réponse HTTP avec le type CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="logs_{screen.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    # Créer le writer CSV
    writer = csv.writer(response)
    writer.writerow(['Date/Heure', 'Action', 'Détails'])

    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.action,
            str(log.details)
        ])

    return response


@login_required
def screen_configuration(request, pk):
    """Configuration d'un écran"""
    from django.contrib import messages

    screen = get_object_or_404(Screen, pk=pk)

    if request.method == 'POST':
        # Mettre à jour la configuration
        # TODO: Implémenter la configuration avancée
        messages.success(request, f'Configuration de l\'écran "{screen.name}" mise à jour.')
        return redirect('screen_detail', pk=screen.pk)

    context = {
        'screen': screen,
        'screens_count': Screen.objects.count(),
    }

    return render(request, 'screens/configuration.html', context)


@login_required
def screen_delete(request, pk):
    """Supprimer un écran"""
    from django.contrib import messages

    screen = get_object_or_404(Screen, pk=pk)

    if request.method == 'POST':
        name = screen.name
        screen.delete()
        messages.success(request, f'L\'écran "{name}" a été supprimé avec succès.')
        return redirect('screens_list')

    context = {
        'screen': screen,
        'screens_count': Screen.objects.count(),
    }

    return render(request, 'screens/delete_confirm.html', context)
