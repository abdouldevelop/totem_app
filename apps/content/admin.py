from django.contrib import admin
from django.utils.html import format_html
from .models import Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'is_active', 'duration', 
                   'file_size_display', 'created_at']
    list_filter = ['content_type', 'is_active', 'created_at']
    search_fields = ['title']
    readonly_fields = ['id', 'file_size', 'checksum', 'created_at', 'updated_at', 'preview']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'content_type', 'is_active', 'duration')
        }),
        ('Fichier', {
            'fields': ('file', 'url', 'preview')
        }),
        ('Informations techniques', {
            'fields': ('file_size', 'checksum'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        if obj.file_size:
            size_mb = obj.file_size / (1024 * 1024)
            if size_mb < 1:
                return f"{obj.file_size / 1024:.2f} KB"
            return f"{size_mb:.2f} MB"
        return "-"
    file_size_display.short_description = 'Taille'
    
    def preview(self, obj):
        if obj.file and obj.content_type == 'image':
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;"/>',
                obj.file.url
            )
        elif obj.url:
            return format_html(
                '<a href="{}" target="_blank">Ouvrir le lien</a>',
                obj.url
            )
        return "Pas d'aperçu disponible"
    preview.short_description = 'Aperçu'
