from rest_framework import serializers
from .models import Playlist, PlaylistItem
from apps.content.serializers import ContentSerializer


class PlaylistItemSerializer(serializers.ModelSerializer):
    content = ContentSerializer(read_only=True)
    content_id = serializers.UUIDField(write_only=True, source='content.id')
    
    class Meta:
        model = PlaylistItem
        fields = ['id', 'order', 'content', 'content_id']


class PlaylistSerializer(serializers.ModelSerializer):
    items = PlaylistItemSerializer(many=True, read_only=True)
    screen_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'description', 'screens', 'is_active',
                  'start_date', 'end_date', 'start_time', 'end_time',
                  'weekdays', 'priority', 'items', 'screen_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_screen_count(self, obj):
        return obj.screens.count()


class PlaylistDetailSerializer(PlaylistSerializer):
    """Serializer avec plus de détails pour la vue détaillée"""
    from apps.screens.serializers import ScreenSerializer
    screens = ScreenSerializer(many=True, read_only=True)
