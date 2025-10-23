from django.db import models

# Create your models here.

class Novel(models.Model):
    title = models.CharField(max_length=255)
    original_language = models.CharField(max_length=50)
    target_language = models.CharField(max_length=50, default='English')
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Chapter(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.IntegerField()
    title = models.CharField(max_length=255)
    original_content = models.TextField()
    translated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.novel.title} - Chapter {self.chapter_number}"

    class Meta:
        ordering = ['chapter_number']
        unique_together = ['novel', 'chapter_number']

