from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Genre, Series, SeriesGenre, Chapter
from .serializers import (
    GenreSerializer, SeriesSerializer, SeriesDetailSerializer,
    SeriesGenreSerializer, ChapterSerializer, ChapterListSerializer
)


class GenreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Genre instances.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'])
    def series(self, request, pk=None):
        """Get all series for this genre"""
        genre = self.get_object()
        series = genre.series.all()
        serializer = SeriesSerializer(series, many=True)
        return Response(serializer.data)


class SeriesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Series instances.
    """
    queryset = Series.objects.all().prefetch_related('genres', 'chapters')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SeriesDetailSerializer
        return SeriesSerializer

    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        """Get all chapters for this series"""
        series = self.get_object()
        chapters = series.chapters.all().order_by('chapter_number')
        serializer = ChapterListSerializer(chapters, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """Filter series by genre name"""
        genre_name = request.query_params.get('genre', None)
        if genre_name:
            series = Series.objects.filter(genres__name__iexact=genre_name)
            serializer = self.get_serializer(series, many=True)
            return Response(serializer.data)
        return Response({'error': 'genre parameter is required'}, status.HTTP_400_BAD_REQUEST)


class SeriesGenreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Series-Genre relationships.
    """
    queryset = SeriesGenre.objects.all()
    serializer_class = SeriesGenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ChapterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Chapter instances.
    """
    queryset = Chapter.objects.all().select_related('series')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['series']
    ordering_fields = ['chapter_number', 'publication_date', 'created_at']
    ordering = ['series', 'chapter_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return ChapterListSerializer
        return ChapterSerializer

    @action(detail=True, methods=['get'])
    def next(self, request, pk=None):
        """Get the next chapter in the series"""
        chapter = self.get_object()
        next_chapter = Chapter.objects.filter(
            series=chapter.series,
            chapter_number=chapter.chapter_number + 1
        ).first()
        if next_chapter:
            serializer = ChapterSerializer(next_chapter)
            return Response(serializer.data)
        return Response({'message': 'No next chapter available'}, status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def previous(self, request, pk=None):
        """Get the previous chapter in the series"""
        chapter = self.get_object()
        prev_chapter = Chapter.objects.filter(
            series=chapter.series,
            chapter_number=chapter.chapter_number - 1
        ).first()
        if prev_chapter:
            serializer = ChapterSerializer(prev_chapter)
            return Response(serializer.data)
        return Response({'message': 'No previous chapter available'}, status.HTTP_404_NOT_FOUND)