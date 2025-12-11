from django.contrib import admin
from .models import ScreenLog


@admin.register(ScreenLog)
class ScreenLogAdmin(admin.ModelAdmin):
    list_display = ['screen', 'action', 'content', 'timestamp']
    list_filter = ['action', 'timestamp', 'screen']
    search_fields = ['screen__name', 'action']
    readonly_fields = ['screen', 'content', 'action', 'details', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
