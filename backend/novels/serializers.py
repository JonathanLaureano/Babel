from rest_framework import serializers
from .models import Novel, Chapter


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'chapter_number', 'title', 'original_content', 
                  'translated_content', 'created_at', 'updated_at']


class NovelSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    
    class Meta:
        model = Novel
        fields = ['id', 'title', 'original_language', 'target_language', 
                  'author', 'description', 'chapters', 'created_at', 'updated_at']


class NovelListSerializer(serializers.ModelSerializer):
    chapter_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Novel
        fields = ['id', 'title', 'original_language', 'target_language', 
                  'author', 'description', 'chapter_count', 'created_at', 'updated_at']
    
    def get_chapter_count(self, obj):
        return obj.chapters.count()
