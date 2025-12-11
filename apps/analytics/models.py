from django.db import models
from apps.screens.models import Screen
from apps.content.models import Content


class ScreenLog(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='logs', verbose_name="Écran")
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Contenu")
    action = models.CharField(max_length=50, verbose_name="Action")
    details = models.JSONField(default=dict, blank=True, verbose_name="Détails")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Log d'écran"
        verbose_name_plural = "Logs d'écrans"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['screen', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.screen.name} - {self.action} - {self.timestamp}"
