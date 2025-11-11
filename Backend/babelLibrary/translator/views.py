"""
API views for the translator app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from threading import Thread
import logging

from .models import TranslationJob
from .serializers import (
    TranslationJobSerializer,
    TranslationJobListSerializer,
    CreateTranslationJobSerializer,
    TranslationJobPreviewSerializer,
    ImportTranslationSerializer,
    TranslatedChapterCacheSerializer,
)
from .translator_service import start_translation_job
from library.models import Series, Chapter, Genre, SeriesGenre

logger = logging.getLogger(__name__)


class TranslationJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing translation jobs.
    
    Endpoints:
    - GET /api/translator/jobs/ - List all translation jobs
    - POST /api/translator/jobs/ - Create new translation job
    - GET /api/translator/jobs/{id}/ - Get job details with chapters
    - GET /api/translator/jobs/{id}/preview/ - Preview translation before import
    - POST /api/translator/jobs/{id}/import/ - Import to library
    - DELETE /api/translator/jobs/{id}/ - Delete a job
    """
    queryset = TranslationJob.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'job_id'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TranslationJobListSerializer
        elif self.action == 'create':
            return CreateTranslationJobSerializer
        elif self.action == 'preview':
            return TranslationJobPreviewSerializer
        elif self.action == 'import_to_library':
            return ImportTranslationSerializer
        return TranslationJobSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new translation job and start processing in background.
        
        Request body:
        {
            "novel_url": "https://...",
            "chapters_requested": 5
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the job
        job = serializer.save()
        
        # Start translation in background thread
        # NOTE: For production, use Celery or similar task queue
        thread = Thread(target=start_translation_job, args=(job.job_id,))
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started translation job {job.job_id} for {job.novel_url}")
        
        # Return job details
        response_serializer = TranslationJobListSerializer(job)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def preview(self, request, job_id=None):
        """
        Preview translated content before importing to library.
        
        Returns novel metadata and list of completed chapters.
        """
        job = self.get_object()
        serializer = self.get_serializer(job)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def import_to_library(self, request, job_id=None):
        """
        Import translated content to library as Series and Chapters.
        
        Request body:
        {
            "cover_image_url": "https://..." (optional),
            "status": "Ongoing" (optional, default: "Ongoing"),
            "selected_chapters": [1, 2, 3] (optional, imports all if not provided)
        }
        """
        job = self.get_object()
        
        serializer = self.get_serializer(
            data=request.data,
            context={'job_id': job.job_id}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Use cover_image_url from request, or fall back to scraped cover_image_url
                cover_url = serializer.validated_data.get('cover_image_url') or job.cover_image_url or ''
                
                # Create Series
                series = Series.objects.create(
                    title=job.english_title,
                    author=job.english_author,
                    description=job.english_description,
                    cover_image_url=cover_url,
                    status=serializer.validated_data.get('status', 'Ongoing'),
                    prompt_dictionary=job.prompt_dictionary
                )
                
                logger.info(f"Created series: {series.title} ({series.series_id})")
                
                # Handle genre
                if job.english_genre:
                    genre, created = Genre.objects.get_or_create(
                        name=job.english_genre
                    )
                    SeriesGenre.objects.create(series=series, genre=genre)
                    logger.info(f"Added genre: {genre.name}")
                
                # Get chapters to import
                selected_chapters = serializer.validated_data.get('selected_chapters')
                if selected_chapters:
                    chapters_to_import = job.cached_chapters.filter(
                        chapter_number__in=selected_chapters,
                        status='polished'
                    ).order_by('chapter_number')
                else:
                    chapters_to_import = job.cached_chapters.filter(
                        status='polished'
                    ).order_by('chapter_number')
                
                # Create Chapters
                chapters_created = 0
                for cache in chapters_to_import:
                    chapter = Chapter.objects.create(
                        series=series,
                        chapter_number=cache.chapter_number,
                        title=cache.english_title,
                        content=cache.english_content_final,
                        word_count=cache.word_count
                    )
                    
                    # Link cache to chapter
                    cache.imported_chapter = chapter
                    cache.save()
                    
                    chapters_created += 1
                    logger.info(f"Created chapter {cache.chapter_number}: {cache.english_title}")
                
                # Link job to series
                job.imported_series = series
                job.save()
                
                logger.info(
                    f"Import completed: {chapters_created} chapters imported to series {series.series_id}"
                )
                
                return Response({
                    'message': 'Successfully imported to library',
                    'series_id': series.series_id,
                    'series_title': series.title,
                    'chapters_imported': chapters_created
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error importing translation job {job.job_id}: {e}")
            return Response(
                {'error': f'Failed to import: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def chapters(self, request, job_id=None):
        """
        Get all cached chapters for a job with full details.
        """
        job = self.get_object()
        chapters = job.cached_chapters.all().order_by('chapter_number')
        serializer = TranslatedChapterCacheSerializer(chapters, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a translation job.
        Only allowed if not yet imported.
        """
        job = self.get_object()
        
        if job.imported_series:
            return Response(
                {'error': 'Cannot delete a job that has been imported to library'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job_id = job.job_id
        job.delete()
        
        logger.info(f"Deleted translation job {job_id}")
        
        return Response(
            {'message': 'Translation job deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
