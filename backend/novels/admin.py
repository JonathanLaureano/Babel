from django.contrib import admin
from .models import Novel, Chapter


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'original_language', 'target_language', 'created_at']
    search_fields = ['title', 'author']
    list_filter = ['original_language', 'target_language']
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['novel', 'chapter_number', 'title', 'created_at']
    search_fields = ['title', 'novel__title']
    list_filter = ['novel']

