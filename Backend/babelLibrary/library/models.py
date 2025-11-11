import uuid
from django.db import models
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Genre(models.Model):
    """Stores unique genre categories."""
    genre_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'genre'

    def __str__(self):
        return self.name


class Series(models.Model):
    """Stores information about each novel series."""
    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Hiatus', 'Hiatus'),
    ]

    series_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cover_image_url = models.URLField(max_length=2048, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Ongoing')
    genres = models.ManyToManyField(Genre, through='SeriesGenre', related_name='series')
    prompt_dictionary = models.JSONField(
        blank=True,
        null=True,
        help_text="Dictionary of terms for consistent translation (e.g., character names, organizations)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'series'
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        """Calculate the average rating from all user ratings."""
        result = self.ratings.aggregate(avg=Avg('rating'))
        return round(result['avg'], 2) if result['avg'] is not None else 0
    
    @property
    def total_view_count(self):
        """Get total unique views for this series including chapter views."""
        # Get unique visitor IDs from both series and chapter views using a single query
        series_visitor_ids = self.series_views.values_list('visitor_id', flat=True)
        chapter_visitor_ids = ChapterView.objects.filter(
            chapter__series=self
        ).values_list('visitor_id', flat=True)
        # Use union to combine and get distinct visitor_ids at the database level
        all_visitor_ids = series_visitor_ids.union(chapter_visitor_ids)
        return all_visitor_ids.count()


class SeriesGenre(models.Model):
    """Resolves the many-to-many relationship between Series and Genre."""
    series_genre_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='series_genres')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='genre_series')

    class Meta:
        db_table = 'seriesgenre'
        unique_together = ('series', 'genre')

    def __str__(self):
        return f"{self.series.title} - {self.genre.name}"


class Chapter(models.Model):
    """Stores details for each chapter within a series."""
    chapter_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.IntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    word_count = models.IntegerField(blank=True, null=True)
    publication_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chapter'
        unique_together = ('series', 'chapter_number')
        ordering = ['series', 'chapter_number']

    def __str__(self):
        return f"{self.series.title} - Chapter {self.chapter_number}: {self.title}"
    
    @property
    def view_count(self):
        """Get total unique views for this chapter."""
        return self.chapter_views.count()


class SeriesRating(models.Model):
    """Stores user ratings for series (1-5 stars)."""
    rating_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='series_ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seriesrating'
        unique_together = ('series', 'user')

    def __str__(self):
        return f"{self.user.username} rated {self.series.title}: {self.rating}/5"


class SeriesView(models.Model):
    """Tracks unique views for series."""
    view_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='series_views')
    visitor_id = models.CharField(max_length=255, help_text="Unique identifier for visitor (user_id or session/IP)")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'seriesview'
        unique_together = ('series', 'visitor_id')
        indexes = [
            models.Index(fields=['series', 'visitor_id']),
        ]

    def __str__(self):
        return f"View of {self.series.title} by {self.visitor_id}"


class ChapterView(models.Model):
    """Tracks unique views for chapters."""
    view_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='chapter_views')
    visitor_id = models.CharField(max_length=255, help_text="Unique identifier for visitor (user_id or session/IP)")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chapterview'
        unique_together = ('chapter', 'visitor_id')
        indexes = [
            models.Index(fields=['chapter', 'visitor_id']),
        ]

    def __str__(self):
        return f"View of {self.chapter.title} by {self.visitor_id}"
