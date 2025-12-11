from django.contrib import admin
from .models import Playlist, PlaylistItem


class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem
    extra = 1
    autocomplete_fields = ['content']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'priority', 'screen_count', 
                   'start_date', 'end_date', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['screens']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [PlaylistItemInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'is_active', 'priority')
        }),
        ('Écrans', {
            'fields': ('screens',)
        }),
        ('Planification', {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time', 'weekdays'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def screen_count(self, obj):
        return obj.screens.count()
    screen_count.short_description = 'Nombre d\'écrans'


@admin.register(PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'content', 'order']
    list_filter = ['playlist']
    search_fields = ['playlist__name', 'content__title']
    autocomplete_fields = ['playlist', 'content']
