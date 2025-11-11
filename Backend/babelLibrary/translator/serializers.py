"""
Serializers for the translator app.
"""
from rest_framework import serializers
from .models import TranslationJob, TranslatedChapterCache


class TranslatedChapterCacheSerializer(serializers.ModelSerializer):
    """Serializer for translated chapter cache."""
    
    class Meta:
        model = TranslatedChapterCache
        fields = [
            'cache_id',
            'chapter_number',
            'chapter_url',
            'korean_title',
            'korean_content',
            'english_title',
            'english_content_raw',
            'english_content_final',
            'word_count',
            'status',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'cache_id',
            'created_at',
            'updated_at',
            'word_count',
        ]


class TranslationJobSerializer(serializers.ModelSerializer):
    """Serializer for translation job list/detail."""
    progress_percentage = serializers.ReadOnlyField()
    cached_chapters = TranslatedChapterCacheSerializer(many=True, read_only=True)
    
    class Meta:
        model = TranslationJob
        fields = [
            'job_id',
            'novel_url',
            'status',
            'korean_title',
            'korean_author',
            'korean_genre',
            'korean_description',
            'cover_image_url',
            'english_title',
            'english_author',
            'english_genre',
            'english_description',
            'prompt_dictionary',
            'chapters_requested',
            'chapters_completed',
            'chapters_failed',
            'progress_percentage',
            'current_operation',
            'error_message',
            'created_at',
            'updated_at',
            'completed_at',
            'imported_series',
            'cached_chapters',
        ]
        read_only_fields = [
            'job_id',
            'status',
            'korean_title',
            'korean_author',
            'korean_genre',
            'korean_description',
            'english_title',
            'english_author',
            'english_genre',
            'english_description',
            'chapters_completed',
            'chapters_failed',
            'progress_percentage',
            'current_operation',
            'error_message',
            'created_at',
            'updated_at',
            'completed_at',
            'imported_series',
        ]


class TranslationJobListSerializer(serializers.ModelSerializer):
    """Simplified serializer for job list (without chapters)."""
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = TranslationJob
        fields = [
            'job_id',
            'novel_url',
            'status',
            'korean_title',
            'english_title',
            'cover_image_url',
            'chapters_requested',
            'chapters_completed',
            'chapters_failed',
            'progress_percentage',
            'current_operation',
            'error_message',
            'created_at',
            'updated_at',
            'completed_at',
            'imported_series',
        ]


class CreateTranslationJobSerializer(serializers.ModelSerializer):
    """Serializer for creating a new translation job."""
    translate_all = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text="If true, translates all available chapters (ignores chapters_requested)"
    )
    
    class Meta:
        model = TranslationJob
        fields = [
            'novel_url',
            'chapters_requested',
            'translate_all',
            'prompt_dictionary',
        ]
    
    def validate(self, data):
        """Validate the job creation request."""
        translate_all = data.get('translate_all', False)
        chapters_requested = data.get('chapters_requested')
        
        # If translate_all is True, chapters_requested will be set later
        if not translate_all:
            if not chapters_requested:
                raise serializers.ValidationError(
                    "Either 'chapters_requested' or 'translate_all=true' must be specified"
                )
            if chapters_requested < 1:
                raise serializers.ValidationError("Must request at least 1 chapter")
            if chapters_requested > 100:
                raise serializers.ValidationError("Cannot request more than 100 chapters at once")
        else:
            # For translate_all, set a placeholder value that will be updated in the service
            # Use 10000 as a marker for "translate all"
            data['chapters_requested'] = 10000
        
        return data
    
    def create(self, validated_data):
        """Create the translation job."""
        # Remove translate_all from validated_data as it's not a model field
        translate_all = validated_data.pop('translate_all', False)
        
        # Create the job
        job = super().create(validated_data)
        
        # Store translate_all flag in the job's current_operation temporarily
        # This is a workaround since we don't have a translate_all field in the model
        if translate_all:
            job.current_operation = 'translate_all'
            job.save()
        
        return job


class TranslationJobPreviewSerializer(serializers.ModelSerializer):
    """Serializer for previewing translation before import."""
    chapters = serializers.SerializerMethodField()
    
    class Meta:
        model = TranslationJob
        fields = [
            'job_id',
            'status',
            'english_title',
            'english_author',
            'english_genre',
            'english_description',
            'chapters_requested',
            'chapters_completed',
            'chapters',
        ]
    
    def get_chapters(self, obj):
        """Get simplified chapter preview data."""
        chapters = obj.cached_chapters.filter(status='polished').order_by('chapter_number')
        return [{
            'cache_id': ch.cache_id,
            'chapter_number': ch.chapter_number,
            'english_title': ch.english_title,
            'word_count': ch.word_count,
            'status': ch.status,
        } for ch in chapters]


class ImportTranslationSerializer(serializers.Serializer):
    """Serializer for importing translated content to library."""
    cover_image_url = serializers.URLField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=['Ongoing', 'Completed', 'Hiatus'],
        default='Ongoing'
    )
    selected_chapters = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        help_text="List of chapter numbers to import. If not provided, all polished chapters will be imported."
    )
    
    def validate(self, data):
        """Validate the import request."""
        job_id = self.context.get('job_id')
        
        if not job_id:
            raise serializers.ValidationError("Job ID is required")
        
        try:
            job = TranslationJob.objects.get(job_id=job_id)
            
            if job.status not in ['completed', 'translating']:
                raise serializers.ValidationError("Job must be completed or in progress to import")
            
            if job.imported_series:
                raise serializers.ValidationError("This job has already been imported")
            
            # Check if selected chapters exist and are polished
            if 'selected_chapters' in data and data['selected_chapters']:
                polished_count = job.cached_chapters.filter(
                    chapter_number__in=data['selected_chapters'],
                    status='polished'
                ).count()
                
                if polished_count != len(data['selected_chapters']):
                    raise serializers.ValidationError(
                        "Some selected chapters are not available or not polished"
                    )
            else:
                # Check if there are any polished chapters
                if not job.cached_chapters.filter(status='polished').exists():
                    raise serializers.ValidationError("No polished chapters available to import")
            
            data['job'] = job
            
        except TranslationJob.DoesNotExist:
            raise serializers.ValidationError("Translation job not found")
        
        return data
