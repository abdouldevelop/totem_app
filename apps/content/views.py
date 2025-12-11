from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Content
from .serializers import ContentSerializer


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'is_active']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Liste des contenus actifs seulement"""
        contents = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(contents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Active/désactive un contenu"""
        content = self.get_object()
        content.is_active = not content.is_active
        content.save()
        serializer = self.get_serializer(content)
        return Response(serializer.data)


# =============================================================================
# VUES WEB POUR LES TEMPLATES HTML
# =============================================================================

@login_required
def content_list(request):
    """Liste de tous les contenus"""
    contents = Content.objects.all().order_by('-created_at')

    # Filtre par type si présent dans la requête
    content_type = request.GET.get('type')
    if content_type:
        contents = contents.filter(content_type=content_type)

    context = {
        'contents': contents,
    }

    return render(request, 'content/list.html', context)


@login_required
def content_create(request):
    """Formulaire de création d'un contenu"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        title = request.POST.get('name')
        description = request.POST.get('description', '')
        content_type = request.POST.get('content_type')
        duration = request.POST.get('duration', 10)
        is_active = request.POST.get('is_active') == 'on'

        # Créer le contenu
        content = Content(
            title=title,
            content_type=content_type,
            duration=int(duration),
            is_active=is_active
        )

        # Gérer le fichier uploadé ou l'URL
        if content_type in ['image', 'video', 'pdf']:
            media_file = request.FILES.get('media_file')
            if media_file:
                content.file = media_file
        elif content_type == 'web':
            url = request.POST.get('url')
            if url:
                content.url = url

        content.save()

        messages.success(request, f'Le contenu "{title}" a été créé avec succès !')
        return redirect('content_list')

    return render(request, 'content/create.html')


@login_required
def content_detail(request, pk):
    """Détails d'un contenu spécifique"""
    content = get_object_or_404(Content, pk=pk)

    context = {
        'content': content,
    }

    return render(request, 'content/detail.html', context)


@login_required
def content_edit(request, pk):
    """Formulaire d'édition d'un contenu"""
    content = get_object_or_404(Content, pk=pk)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        content.title = request.POST.get('name')
        content.content_type = request.POST.get('content_type')
        content.duration = int(request.POST.get('duration', 10))
        content.is_active = request.POST.get('is_active') == 'on'

        # Gérer le fichier uploadé ou l'URL
        if content.content_type in ['image', 'video', 'pdf']:
            media_file = request.FILES.get('media_file')
            if media_file:
                content.file = media_file
        elif content.content_type == 'web':
            url = request.POST.get('url')
            if url:
                content.url = url

        content.save()

        messages.success(request, f'Le contenu "{content.title}" a été modifié avec succès !')
        return redirect('content_detail', pk=content.pk)

    context = {
        'content': content,
    }

    return render(request, 'content/edit.html', context)


@login_required
def content_delete(request, pk):
    """Suppression d'un contenu"""
    content = get_object_or_404(Content, pk=pk)

    if request.method == 'POST':
        title = content.title
        content.delete()
        messages.success(request, f'Le contenu "{title}" a été supprimé avec succès !')
        return redirect('content_list')

    context = {
        'content': content,
    }

    return render(request, 'content/delete_confirm.html', context)
