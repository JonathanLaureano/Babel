from rest_framework import serializers
from .models import Genre, Series, SeriesGenre, Chapter, SeriesRating


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
    view_count = serializers.IntegerField(source='view_count_annotation', read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'chapter_id', 'series', 'series_title', 'chapter_number', 
            'title', 'content', 'word_count', 'publication_date',
            'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['chapter_id', 'view_count', 'created_at', 'updated_at']


class ChapterListSerializer(serializers.ModelSerializer):
    """Serializer for listing chapters without full content"""
    series_title = serializers.CharField(source='series.title', read_only=True)
    view_count = serializers.IntegerField(source='view_count_annotation', read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'chapter_id', 'series', 'series_title', 'chapter_number', 
            'title', 'word_count', 'publication_date', 'view_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['chapter_id', 'view_count', 'created_at', 'updated_at']


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
    average_rating = serializers.FloatField(source='avg_rating', read_only=True)
    total_view_count = serializers.IntegerField(source='total_views', read_only=True)

    class Meta:
        model = Series
        fields = [
            'series_id', 'title', 'author', 'description', 'cover_image_url', 
            'status', 'genres', 'genre_ids', 'chapters_count', 'average_rating',
            'total_view_count', 'prompt_dictionary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['series_id', 'average_rating', 'total_view_count', 'created_at', 'updated_at']

    def get_chapters_count(self, obj):
        return obj.chapters.count()


class SeriesDetailSerializer(SeriesSerializer):
    """Detailed serializer including chapters list"""
    chapters = ChapterListSerializer(many=True, read_only=True)

    class Meta(SeriesSerializer.Meta):
        fields = SeriesSerializer.Meta.fields + ['chapters']


class SeriesRatingSerializer(serializers.ModelSerializer):
    """Serializer for rating a series."""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SeriesRating
        fields = ['rating_id', 'series', 'user', 'user_username', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['rating_id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value
