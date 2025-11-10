"""
Django admin configuration for translator app.
"""
from django.contrib import admin
from .models import TranslationJob, TranslatedChapterCache


@admin.register(TranslationJob)
class TranslationJobAdmin(admin.ModelAdmin):
    """Admin interface for TranslationJob."""
    list_display = [
        'job_id',
        'english_title',
        'status',
        'chapters_completed',
        'chapters_requested',
        'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['english_title', 'korean_title', 'novel_url']
    readonly_fields = [
        'job_id',
        'created_at',
        'updated_at',
        'completed_at',
        'progress_percentage',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'job_id',
                'novel_url',
                'status',
                'current_operation',
                'error_message',
            )
        }),
        ('Korean Metadata', {
            'fields': (
                'korean_title',
                'korean_author',
                'korean_genre',
                'korean_description',
            )
        }),
        ('English Metadata', {
            'fields': (
                'english_title',
                'english_author',
                'english_genre',
                'english_description',
            )
        }),
        ('Progress', {
            'fields': (
                'chapters_requested',
                'chapters_completed',
                'chapters_failed',
                'progress_percentage',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
            )
        }),
        ('Import', {
            'fields': ('imported_series',)
        }),
    )


@admin.register(TranslatedChapterCache)
class TranslatedChapterCacheAdmin(admin.ModelAdmin):
    """Admin interface for TranslatedChapterCache."""
    list_display = [
        'cache_id',
        'job',
        'chapter_number',
        'english_title',
        'status',
        'word_count',
    ]
    list_filter = ['status', 'job']
    search_fields = ['english_title', 'korean_title', 'job__english_title']
    readonly_fields = [
        'cache_id',
        'created_at',
        'updated_at',
        'word_count',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'cache_id',
                'job',
                'chapter_number',
                'chapter_url',
                'status',
                'error_message',
            )
        }),
        ('Korean Content', {
            'fields': (
                'korean_title',
                'korean_content',
            )
        }),
        ('English Content', {
            'fields': (
                'english_title',
                'english_content_raw',
                'english_content_final',
                'word_count',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
        ('Import', {
            'fields': ('imported_chapter',)
        }),
    )
