import uuid
from django.db import models
from django.core.validators import MinValueValidator


class TranslationJob(models.Model):
    """Tracks translation jobs from Korean novel websites."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scraping', 'Scraping Novel Info'),
        ('translating', 'Translating Chapters'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    novel_url = models.URLField(max_length=2048, help_text="URL of the novel page to scrape")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Novel metadata (Korean)
    korean_title = models.CharField(max_length=255, blank=True, null=True)
    korean_author = models.CharField(max_length=255, blank=True, null=True)
    korean_genre = models.CharField(max_length=100, blank=True, null=True)
    korean_description = models.TextField(blank=True, null=True)
    cover_image_url = models.URLField(max_length=2048, blank=True, null=True, help_text="Cover image URL from source")
    
    # Novel metadata (English - translated)
    english_title = models.CharField(max_length=255, blank=True, null=True)
    english_author = models.CharField(max_length=255, blank=True, null=True)
    english_genre = models.CharField(max_length=100, blank=True, null=True)
    english_description = models.TextField(blank=True, null=True)
    
    # Translation consistency
    prompt_dictionary = models.JSONField(
        blank=True,
        null=True,
        help_text="Dictionary of terms for consistent translation (e.g., character names, organizations, special terms)"
    )
    
    # Progress tracking
    chapters_requested = models.IntegerField(validators=[MinValueValidator(1)], help_text="Number of chapters to translate")
    chapters_completed = models.IntegerField(default=0, help_text="Number of chapters successfully translated")
    chapters_failed = models.IntegerField(default=0, help_text="Number of chapters that failed")
    
    # Status messages
    current_operation = models.CharField(max_length=255, blank=True, null=True, help_text="Current operation being performed")
    error_message = models.TextField(blank=True, null=True, help_text="Error message if job failed")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True, help_text="When the job completed or failed")
    
    # Link to created series (after import)
    imported_series = models.ForeignKey(
        'library.Series',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='translation_jobs',
        help_text="Series created from this translation job"
    )

    class Meta:
        db_table = 'translationjob'
        ordering = ['-created_at']

    def __str__(self):
        title = self.english_title or self.korean_title or 'Unknown'
        return f"Translation Job: {title} ({self.status})"
    
    @property
    def progress_percentage(self):
        """Calculate completion percentage."""
        if self.chapters_requested == 0:
            return 0
        return (self.chapters_completed / self.chapters_requested) * 100


class TranslatedChapterCache(models.Model):
    """Caches translated chapter content before importing to library."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scraped', 'Scraped'),
        ('translated', 'Translated'),
        ('polished', 'Polished'),
        ('failed', 'Failed'),
    ]

    cache_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(TranslationJob, on_delete=models.CASCADE, related_name='cached_chapters')
    
    # Chapter identification
    chapter_number = models.IntegerField(validators=[MinValueValidator(1)])
    chapter_url = models.URLField(max_length=2048, help_text="Original chapter URL")
    
    # Korean (original)
    korean_title = models.CharField(max_length=255)
    korean_content = models.TextField()
    
    # English (translated)
    english_title = models.CharField(max_length=255, blank=True, null=True)
    english_content_raw = models.TextField(blank=True, null=True, help_text="Raw translation before polishing")
    english_content_final = models.TextField(blank=True, null=True, help_text="Final polished translation")
    
    # Metadata
    word_count = models.IntegerField(blank=True, null=True, help_text="Word count of final English content")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to imported chapter
    imported_chapter = models.ForeignKey(
        'library.Chapter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='translation_cache',
        help_text="Chapter created from this cache"
    )

    class Meta:
        db_table = 'translatedchaptercache'
        unique_together = ('job', 'chapter_number')
        ordering = ['job', 'chapter_number']

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.english_title or self.korean_title} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Calculate word count if final content exists
        if self.english_content_final and not self.word_count:
            self.word_count = len(self.english_content_final.split())
        super().save(*args, **kwargs)
