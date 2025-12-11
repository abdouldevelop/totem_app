from django.contrib import admin
from django.utils.html import format_html
from .models import Screen


@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'status_badge', 'is_online_badge', 
                   'last_heartbeat', 'app_version', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'location', 'api_token']
    readonly_fields = ['id', 'api_token', 'last_heartbeat', 'created_at', 'updated_at', 'device_info_display']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'location', 'tags', 'status')
        }),
        ('Authentification', {
            'fields': ('api_token',)
        }),
        ('Informations techniques', {
            'fields': ('app_version', 'device_info_display', 'last_heartbeat')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'orange',
            'offline': 'red'
        }
        return format_html(
            '<span style="color: {};">●</span> {}',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def is_online_badge(self, obj):
        if obj.is_online():
            return format_html('<span style="color: green;">✓ En ligne</span>')
        return format_html('<span style="color: red;">✗ Hors ligne</span>')
    is_online_badge.short_description = 'Connexion'
    
    def device_info_display(self, obj):
        if not obj.device_info:
            return "Aucune information"
        info = []
        for key, value in obj.device_info.items():
            info.append(f"<strong>{key}:</strong> {value}")
        return format_html("<br>".join(info))
    device_info_display.short_description = 'Informations de l\'appareil'
