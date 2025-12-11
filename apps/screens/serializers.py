from rest_framework import serializers
from .models import Screen


class ScreenSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = Screen
        fields = ['id', 'name', 'location', 'status', 'is_online',
                  'last_heartbeat', 'app_version', 'device_info', 
                  'tags', 'created_at', 'updated_at']
        read_only_fields = ['id', 'last_heartbeat', 'created_at', 'updated_at']
    
    def get_is_online(self, obj):
        return obj.is_online()


class ScreenRegisterSerializer(serializers.Serializer):
    device_info = serializers.JSONField(required=False)
    app_version = serializers.CharField(max_length=20, default='1.0.0')
