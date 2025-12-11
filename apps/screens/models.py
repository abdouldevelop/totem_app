from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid


class Screen(models.Model):
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('offline', 'Hors ligne'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nom")
    location = models.CharField(max_length=300, verbose_name="Emplacement")
    description = models.TextField(blank=True, verbose_name="Description")
    api_token = models.CharField(max_length=100, unique=True, verbose_name="Token API")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name="Statut")
    last_heartbeat = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    app_version = models.CharField(max_length=20, blank=True, verbose_name="Version de l'app")
    device_info = models.JSONField(default=dict, blank=True, verbose_name="Info appareil")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Tags", 
                           help_text="Tags séparés par des virgules")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Écran"
        verbose_name_plural = "Écrans"
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def is_online(self):
        if not self.last_heartbeat:
            return False
        return timezone.now() - self.last_heartbeat < timedelta(minutes=5)
    
    def save(self, *args, **kwargs):
        if not self.api_token:
            self.api_token = str(uuid.uuid4())
        super().save(*args, **kwargs)
