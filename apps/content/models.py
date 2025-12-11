from django.db import models
import uuid
import hashlib


class ContentType(models.TextChoices):
    IMAGE = 'image', 'Image'
    VIDEO = 'video', 'Vidéo'
    PDF = 'pdf', 'PDF'
    WEB = 'web', 'Page Web'


class Content(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300, verbose_name="Titre")
    content_type = models.CharField(max_length=20, choices=ContentType.choices, verbose_name="Type")
    file = models.FileField(upload_to='content/%Y/%m/', null=True, blank=True, verbose_name="Fichier")
    url = models.URLField(blank=True, null=True, verbose_name="URL", 
                         help_text="Pour les contenus web")
    duration = models.IntegerField(default=10, verbose_name="Durée", 
                                  help_text="Durée d'affichage en secondes")
    file_size = models.BigIntegerField(default=0, verbose_name="Taille du fichier")
    checksum = models.CharField(max_length=64, blank=True, verbose_name="Checksum")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contenu"
        verbose_name_plural = "Contenus"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.file:
            # Calculer le checksum MD5
            self.file.seek(0)
            md5_hash = hashlib.md5()
            for chunk in self.file.chunks():
                md5_hash.update(chunk)
            self.checksum = md5_hash.hexdigest()
            self.file.seek(0)
            self.file_size = self.file.size
        super().save(*args, **kwargs)
