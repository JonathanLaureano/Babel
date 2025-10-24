from rest_framework import serializers
from .models import Genre, Series, SeriesGenre, Chapter


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genre_id', 'name']
        read_only_fields = ['genre_id']


class SeriesGenreSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    series_title = serializers.CharField(source='series.title', read_only=True)

    class Meta:
        model = SeriesGenre
        fields = ['series_genre_id', 'series', 'series_title', 'genre', 'genre_name']
        read_only_fields = ['series_genre_id']


class ChapterSerializer(serializers.ModelSerializer):
    series_title = serializers.CharField(source='series.title', read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'chapter_id', 'series', 'series_title', 'chapter_number', 
            'title', 'content', 'word_count', 'publication_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['chapter_id', 'created_at', 'updated_at']


class ChapterListSerializer(serializers.ModelSerializer):
    """Serializer for listing chapters without full content"""
    series_title = serializers.CharField(source='series.title', read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'chapter_id', 'series', 'series_title', 'chapter_number', 
            'title', 'word_count', 'publication_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['chapter_id', 'created_at', 'updated_at']


class SeriesSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Genre.objects.all(), 
        source='genres', 
        write_only=True,
        required=False
    )
    chapters_count = serializers.SerializerMethodField()

    class Meta:
        model = Series
        fields = [
            'series_id', 'title', 'description', 'cover_image_url', 
            'status', 'genres', 'genre_ids', 'chapters_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['series_id', 'created_at', 'updated_at']

    def get_chapters_count(self, obj):
        return obj.chapters.count()


class SeriesDetailSerializer(SeriesSerializer):
    """Detailed serializer including chapters list"""
    chapters = ChapterListSerializer(many=True, read_only=True)

    class Meta(SeriesSerializer.Meta):
        fields = SeriesSerializer.Meta.fields + ['chapters']
