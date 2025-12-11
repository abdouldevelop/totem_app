from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Playlist, PlaylistItem
from .serializers import PlaylistSerializer, PlaylistDetailSerializer, PlaylistItemSerializer
from apps.content.models import Content
from apps.screens.models import Screen


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlaylistDetailSerializer
        return PlaylistSerializer
    
    @action(detail=True, methods=['post'])
    def add_content(self, request, pk=None):
        """Ajoute un contenu à la playlist"""
        playlist = self.get_object()
        content_id = request.data.get('content_id')
        order = request.data.get('order', playlist.items.count())
        
        try:
            content = Content.objects.get(id=content_id)
            item, created = PlaylistItem.objects.get_or_create(
                playlist=playlist,
                content=content,
                defaults={'order': order}
            )
            
            if not created:
                return Response(
                    {'error': 'Ce contenu est déjà dans la playlist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = PlaylistItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Content.DoesNotExist:
            return Response(
                {'error': 'Contenu non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_content(self, request, pk=None):
        """Retire un contenu de la playlist"""
        playlist = self.get_object()
        content_id = request.data.get('content_id')
        
        try:
            item = PlaylistItem.objects.get(playlist=playlist, content_id=content_id)
            item.delete()
            return Response({'status': 'Contenu retiré'})
        except PlaylistItem.DoesNotExist:
            return Response(
                {'error': 'Contenu non trouvé dans la playlist'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Réorganise l'ordre des contenus"""
        playlist = self.get_object()
        order_data = request.data.get('order', [])
        
        # order_data doit être une liste de {content_id, order}
        for item_data in order_data:
            try:
                item = PlaylistItem.objects.get(
                    playlist=playlist,
                    content_id=item_data['content_id']
                )
                item.order = item_data['order']
                item.save()
            except (PlaylistItem.DoesNotExist, KeyError):
                continue
        
        serializer = self.get_serializer(playlist)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplique une playlist"""
        playlist = self.get_object()
        new_playlist = Playlist.objects.create(
            name=f"{playlist.name} (Copie)",
            description=playlist.description,
            is_active=False,
            start_date=playlist.start_date,
            end_date=playlist.end_date,
            start_time=playlist.start_time,
            end_time=playlist.end_time,
            weekdays=playlist.weekdays,
            priority=playlist.priority
        )
        
        # Copier les items
        for item in playlist.items.all():
            PlaylistItem.objects.create(
                playlist=new_playlist,
                content=item.content,
                order=item.order
            )
        
        serializer = self.get_serializer(new_playlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# =============================================================================
# VUES WEB POUR LES TEMPLATES HTML
# =============================================================================

@login_required
def playlists_list(request):
    """Liste de toutes les playlists"""
    playlists = Playlist.objects.all().order_by('-created_at')

    # Ajouter le nombre de contenus et d'écrans pour chaque playlist
    playlists = playlists.annotate(
        contents_count=Count('items', distinct=True),
        screens_count=Count('screens', distinct=True)
    )

    # Statistiques
    active_playlists_count = Playlist.objects.filter(is_active=True).count()
    scheduled_playlists_count = Playlist.objects.exclude(
        start_date__isnull=True
    ).count()
    total_contents_count = Content.objects.count()
    assigned_screens_count = Screen.objects.exclude(
        playlists__isnull=True
    ).distinct().count()

    context = {
        'playlists': playlists,
        'active_playlists_count': active_playlists_count,
        'scheduled_playlists_count': scheduled_playlists_count,
        'total_contents_count': total_contents_count,
        'assigned_screens_count': assigned_screens_count,
    }

    return render(request, 'playlists/list.html', context)


@login_required
def playlist_create(request):
    """Formulaire de création d'une playlist"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        # Dates et heures
        schedule_start_date = request.POST.get('schedule_start_date') or None
        schedule_end_date = request.POST.get('schedule_end_date') or None
        schedule_start_time = request.POST.get('schedule_start_time') or None
        schedule_end_time = request.POST.get('schedule_end_time') or None

        # Jours de la semaine
        days = request.POST.getlist('days[]')
        weekdays = ','.join(days) if days else '0,1,2,3,4,5,6'

        # Créer la playlist
        playlist = Playlist.objects.create(
            name=name,
            description=description,
            is_active=is_active,
            start_date=schedule_start_date,
            end_date=schedule_end_date,
            start_time=schedule_start_time,
            end_time=schedule_end_time,
            weekdays=weekdays
        )

        # Assigner les écrans sélectionnés
        screens_ids = request.POST.getlist('screens[]')
        for screen_id in screens_ids:
            try:
                screen = Screen.objects.get(id=screen_id)
                playlist.screens.add(screen)
            except Screen.DoesNotExist:
                pass

        # Ajouter les contenus sélectionnés
        contents_ids = request.POST.getlist('contents[]')
        for i, content_id in enumerate(contents_ids):
            try:
                content = Content.objects.get(id=content_id)
                PlaylistItem.objects.create(
                    playlist=playlist,
                    content=content,
                    order=i
                )
            except Content.DoesNotExist:
                pass

        messages.success(request, f'La playlist "{name}" a été créée avec succès !')
        return redirect('playlists_list')

    # GET request - afficher le formulaire
    contents = Content.objects.filter(is_active=True).order_by('-created_at')
    screens = Screen.objects.all().order_by('name')

    context = {
        'contents': contents,
        'screens': screens,
    }

    return render(request, 'playlists/create.html', context)


@login_required
def playlist_detail(request, pk):
    """Détails d'une playlist spécifique"""
    playlist = get_object_or_404(Playlist, pk=pk)

    # Items de la playlist
    playlist_items = playlist.items.select_related('content').order_by('order')

    # Écrans assignés
    assigned_screens = playlist.screens.all()

    context = {
        'playlist': playlist,
        'playlist_items': playlist_items,
        'assigned_screens': assigned_screens,
    }

    return render(request, 'playlists/detail.html', context)


@login_required
def playlist_edit(request, pk):
    """Formulaire d'édition d'une playlist"""
    playlist = get_object_or_404(Playlist, pk=pk)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        playlist.name = request.POST.get('name')
        playlist.description = request.POST.get('description', '')
        playlist.is_active = request.POST.get('is_active') == 'on'

        # Dates et heures
        playlist.start_date = request.POST.get('schedule_start_date') or None
        playlist.end_date = request.POST.get('schedule_end_date') or None
        playlist.start_time = request.POST.get('schedule_start_time') or None
        playlist.end_time = request.POST.get('schedule_end_time') or None

        # Jours de la semaine
        days = request.POST.getlist('days[]')
        playlist.weekdays = ','.join(days) if days else '0,1,2,3,4,5,6'

        # Priorité
        priority = request.POST.get('priority', 0)
        playlist.priority = int(priority) if priority else 0

        playlist.save()

        # Gérer les écrans assignés
        screens_ids = request.POST.getlist('screens[]')

        # Supprimer toutes les assignations existantes
        playlist.screens.clear()

        # Ajouter les nouveaux écrans sélectionnés
        for screen_id in screens_ids:
            try:
                screen = Screen.objects.get(id=screen_id)
                playlist.screens.add(screen)
            except Screen.DoesNotExist:
                pass

        # Gérer les contenus sélectionnés
        contents_ids = request.POST.getlist('contents[]')

        # Supprimer tous les items existants
        playlist.items.all().delete()

        # Ajouter les nouveaux contenus sélectionnés
        for i, content_id in enumerate(contents_ids):
            try:
                content = Content.objects.get(id=content_id)
                PlaylistItem.objects.create(
                    playlist=playlist,
                    content=content,
                    order=i
                )
            except Content.DoesNotExist:
                pass

        messages.success(request, f'La playlist "{playlist.name}" a été modifiée avec succès !')
        return redirect('playlist_detail', pk=playlist.pk)

    # GET request - afficher le formulaire
    weekdays = [
        ('0', 'Lundi'),
        ('1', 'Mardi'),
        ('2', 'Mercredi'),
        ('3', 'Jeudi'),
        ('4', 'Vendredi'),
        ('5', 'Samedi'),
        ('6', 'Dimanche'),
    ]

    # Récupérer tous les écrans
    available_screens = Screen.objects.all().order_by('name')

    # Récupérer les IDs des écrans actuellement assignés à la playlist
    selected_screen_ids = list(playlist.screens.values_list('id', flat=True))

    # Récupérer tous les contenus actifs
    available_contents = Content.objects.filter(is_active=True).order_by('-created_at')

    # Récupérer les IDs des contenus actuellement dans la playlist
    selected_content_ids = list(playlist.items.values_list('content_id', flat=True))

    context = {
        'playlist': playlist,
        'weekdays': weekdays,
        'available_screens': available_screens,
        'selected_screen_ids': selected_screen_ids,
        'available_contents': available_contents,
        'selected_content_ids': selected_content_ids,
    }

    return render(request, 'playlists/edit.html', context)


@login_required
def playlist_delete(request, pk):
    """Suppression d'une playlist"""
    playlist = get_object_or_404(Playlist, pk=pk)

    if request.method == 'POST':
        name = playlist.name
        playlist.delete()
        messages.success(request, f'La playlist "{name}" a été supprimée avec succès !')
        return redirect('playlists_list')

    context = {
        'playlist': playlist,
    }

    return render(request, 'playlists/delete_confirm.html', context)
