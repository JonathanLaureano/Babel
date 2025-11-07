from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from .models import Genre, Series, SeriesGenre, Chapter, SeriesRating, SeriesView, ChapterView
from .serializers import (
    GenreSerializer, SeriesSerializer, SeriesDetailSerializer,
    SeriesGenreSerializer, ChapterSerializer, ChapterListSerializer, SeriesRatingSerializer
)


class GenreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Genre instances.
    """
    queryset = Genre.objects.all()
    pagination_class = None
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
    queryset = Series.objects.all().prefetch_related('genres', 'chapters').annotate(
        avg_rating=Avg('ratings__rating'),
        total_views=Count('views__visitor_id', distinct=True) + Count('chapters__chapter_views__visitor_id', distinct=True)
    )
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Allow anonymous access to list and retrieve actions.
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

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
        return Response({'error': 'genre parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a series (1-5 stars). Requires authentication."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to rate a series'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        series = self.get_object()
        rating_value = request.data.get('rating')
        
        if not rating_value:
            return Response(
                {'error': 'Rating value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'Rating must be an integer between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has already rated
        existing_rating = SeriesRating.objects.filter(
            series=series,
            user=request.user
        ).first()
        
        if existing_rating:
            return Response(
                {'error': 'You have already rated this series'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new rating
        rating = SeriesRating.objects.create(
            series=series,
            user=request.user,
            rating=rating_value
        )
        
        serializer = SeriesRatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def track_view(self, request, pk=None):
        """Track a view for this series."""
        series = self.get_object()
        
        # Get visitor ID (user ID if authenticated, otherwise session/IP)
        if request.user.is_authenticated:
            visitor_id = f"user_{request.user.user_id}"
        else:
            # Use session key or IP address as fallback
            visitor_id = request.session.session_key
            if not visitor_id:
                # Create session if it doesn't exist
                request.session.create()
                visitor_id = request.session.session_key
            if not visitor_id:
                # Fallback to IP
                visitor_id = self._get_client_ip(request)
        
        # Create or get view (unique constraint prevents duplicates)
        view, created = SeriesView.objects.get_or_create(
            series=series,
            visitor_id=visitor_id
        )
        
        return Response({
            'message': 'View tracked' if created else 'View already recorded',
            'view_count': series.total_view_count
        }, status=status.HTTP_200_OK)

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
    queryset = Chapter.objects.all().select_related('series').annotate(
        view_count_annotation=Count('chapter_views', distinct=True)
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['series']
    ordering_fields = ['chapter_number', 'publication_date', 'created_at']
    ordering = ['series', 'chapter_number']

    def get_permissions(self):
        """
        Allow anonymous access to list and retrieve actions.
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

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
        return Response({'message': 'No next chapter available'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response({'message': 'No previous chapter available'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def track_view(self, request, pk=None):
        """Track a view for this chapter."""
        chapter = self.get_object()
        
        # Get visitor ID (user ID if authenticated, otherwise session/IP)
        if request.user.is_authenticated:
            visitor_id = f"user_{request.user.user_id}"
        else:
            # Use session key or IP address as fallback
            visitor_id = request.session.session_key
            if not visitor_id:
                # Create session if it doesn't exist
                request.session.create()
                visitor_id = request.session.session_key
            if not visitor_id:
                # Fallback to IP
                visitor_id = self._get_client_ip(request)
        
        # Create or get view (unique constraint prevents duplicates)
        view, created = ChapterView.objects.get_or_create(
            chapter=chapter,
            visitor_id=visitor_id
        )
        
        return Response({
            'message': 'View tracked' if created else 'View already recorded',
            'view_count': chapter.view_count
        }, status=status.HTTP_200_OK)

class ViewTrackingMixin:
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the last IP (closest proxy)
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
