from django.contrib import admin
from .models import Genre, Series, SeriesGenre, Chapter, SeriesRating, SeriesView, ChapterView


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'genre_id']
    search_fields = ['name']


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'author', 'description']
    readonly_fields = ['series_id', 'created_at', 'updated_at', 'average_rating', 'total_view_count']


@admin.register(SeriesGenre)
class SeriesGenreAdmin(admin.ModelAdmin):
    list_display = ['series', 'genre']
    list_filter = ['genre']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'series', 'chapter_number', 'publication_date']
    list_filter = ['series']
    search_fields = ['title', 'series__title']
    readonly_fields = ['chapter_id', 'created_at', 'updated_at', 'view_count']


@admin.register(SeriesRating)
class SeriesRatingAdmin(admin.ModelAdmin):
    list_display = ['series', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['series__title', 'user__username']
    readonly_fields = ['rating_id', 'created_at', 'updated_at']


@admin.register(SeriesView)
class SeriesViewAdmin(admin.ModelAdmin):
    list_display = ['series', 'visitor_id', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['series__title', 'visitor_id']
    readonly_fields = ['view_id', 'viewed_at']


@admin.register(ChapterView)
class ChapterViewAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'visitor_id', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['chapter__title', 'visitor_id']
    readonly_fields = ['view_id', 'viewed_at']
