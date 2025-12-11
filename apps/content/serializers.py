from rest_framework import serializers
from .models import Content


class ContentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Content
        fields = ['id', 'title', 'content_type', 'file', 'file_url', 'url', 
                  'duration', 'file_size', 'checksum', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'file_size', 'checksum', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
