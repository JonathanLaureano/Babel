import uuid
from django.db import models


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
    description = models.TextField(blank=True, null=True)
    cover_image_url = models.URLField(max_length=2048, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Ongoing')
    genres = models.ManyToManyField(Genre, through='SeriesGenre', related_name='series')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'series'
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.title


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
