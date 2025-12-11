from django.db import models
from apps.screens.models import Screen
from apps.content.models import Content
import uuid


class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    screens = models.ManyToManyField(Screen, related_name='playlists', verbose_name="Écrans")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    # Planification
    start_date = models.DateField(null=True, blank=True, verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    start_time = models.TimeField(null=True, blank=True, verbose_name="Heure de début")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Heure de fin")
    
    # Jours de la semaine (0=lundi, 6=dimanche)
    weekdays = models.CharField(max_length=50, default='0,1,2,3,4,5,6', verbose_name="Jours de la semaine",
                               help_text="0=Lundi, 6=Dimanche. Séparés par des virgules")
    
    priority = models.IntegerField(default=0, verbose_name="Priorité",
                                  help_text="Plus le nombre est élevé, plus la priorité est haute")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifiée le")
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"
    
    def __str__(self):
        return self.name

    @property
    def contents(self):
        """Retourne un queryset des contenus de la playlist triés par ordre"""
        return Content.objects.filter(
            playlistitem__playlist=self
        ).order_by('playlistitem__order')


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='items', verbose_name="Playlist")
    content = models.ForeignKey(Content, on_delete=models.CASCADE, verbose_name="Contenu")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    
    class Meta:
        ordering = ['order']
        unique_together = ['playlist', 'content']
        verbose_name = "Élément de playlist"
        verbose_name_plural = "Éléments de playlist"
    
    def __str__(self):
        return f"{self.playlist.name} - {self.content.title}"
